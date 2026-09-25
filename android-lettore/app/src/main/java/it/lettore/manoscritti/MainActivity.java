package it.lettore.manoscritti;

import android.Manifest;
import android.app.Activity;
import android.content.ContentValues;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.speech.tts.Voice;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Locale;

/**
 * Contenitore Android della web app "Lettore di manoscritti".
 * La pagina viene servita dagli asset su un indirizzo https fittizio, così il browser
 * interno la considera sicura (necessario per microfono e IndexedDB).
 * Aggiunge ciò che la WebView non offre: sintesi vocale e salvataggio in Download.
 */
public class MainActivity extends Activity {
    private static final String HOST = "appassets.androidplatform.net";
    private static final String INDIRIZZO = "https://" + HOST + "/index.html";
    private static final int RICHIESTA_FILE = 1;
    private static final int RICHIESTA_MICROFONO = 2;

    private WebView webView;
    private TextToSpeech tts;
    private volatile int statoTts = -1; // -1 in avvio, 0 pronta, 1 senza italiano, 2 non disponibile
    private String voceAttuale = "";
    private ValueCallback<Uri[]> sceltaFile;
    private PermissionRequest richiestaMicrofono;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.TRANSPARENT);
        setContentView(webView);

        WebSettings impostazioni = webView.getSettings();
        impostazioni.setJavaScriptEnabled(true);
        impostazioni.setDomStorageEnabled(true);
        impostazioni.setMediaPlaybackRequiresUserGesture(false);
        impostazioni.setAllowFileAccess(false);
        impostazioni.setAllowContentAccess(true);

        webView.setWebViewClient(new ClientPagina());
        webView.setWebChromeClient(new ClientBrowser());
        webView.addJavascriptInterface(new Ponte(), "AndroidApp");

        tts = new TextToSpeech(this, stato -> {
            if (stato != TextToSpeech.SUCCESS) { statoTts = 2; return; }
            int lingua = tts.setLanguage(Locale.ITALY);
            statoTts = (lingua == TextToSpeech.LANG_MISSING_DATA || lingua == TextToSpeech.LANG_NOT_SUPPORTED) ? 1 : 0;
            avvisaVociCambiate();
        });
        tts.setOnUtteranceProgressListener(new UtteranceProgressListener() {
            @Override public void onStart(String id) {}
            @Override public void onDone(String id) { evento(id, "end"); }
            @Override public void onError(String id) { evento(id, "synthesis-failed"); }
            @Override public void onStop(String id, boolean interrotto) { evento(id, "interrupted"); }
        });

        if (savedInstanceState != null) webView.restoreState(savedInstanceState);
        else webView.loadUrl(INDIRIZZO);
    }

    private void avvisaVociCambiate() {
        runOnUiThread(() -> webView.evaluateJavascript("window.__vociCambiate && window.__vociCambiate()", null));
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Al ritorno dalle impostazioni potrebbero esserci voci nuove.
        if (statoTts >= 0) avvisaVociCambiate();
    }

    private void evento(String id, String tipo) {
        // Gli id sono generati dalla pagina (lettere e cifre): nessun rischio di iniezione.
        if (id == null || !id.matches("[A-Za-z0-9]+")) return;
        runOnUiThread(() -> webView.evaluateJavascript(
                "window.__ttsEvento && window.__ttsEvento('" + id + "','" + tipo + "')", null));
    }

    /** Serve la pagina dagli asset e apre i link esterni nel browser. */
    private class ClientPagina extends WebViewClient {
        @Override
        public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest richiesta) {
            Uri uri = richiesta.getUrl();
            if (!HOST.equals(uri.getHost())) return null;
            String percorso = uri.getPath() == null || uri.getPath().equals("/") ? "index.html" : uri.getPath().substring(1);
            try {
                InputStream dati = getAssets().open(percorso);
                return new WebResourceResponse(tipoMime(percorso), "utf-8", dati);
            } catch (IOException e) {
                WebResourceResponse assente = new WebResourceResponse("text/plain", "utf-8", null);
                assente.setStatusCodeAndReasonPhrase(404, "Not Found");
                return assente;
            }
        }

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest richiesta) {
            Uri uri = richiesta.getUrl();
            if (HOST.equals(uri.getHost())) return false;
            try { startActivity(new Intent(Intent.ACTION_VIEW, uri)); } catch (Exception ignorata) {}
            return true;
        }
    }

    private static String tipoMime(String percorso) {
        if (percorso.endsWith(".html")) return "text/html";
        if (percorso.endsWith(".js")) return "application/javascript";
        if (percorso.endsWith(".css")) return "text/css";
        if (percorso.endsWith(".png")) return "image/png";
        return "application/octet-stream";
    }

    /** Microfono e scelta dei file. */
    private class ClientBrowser extends WebChromeClient {
        @Override
        public void onPermissionRequest(PermissionRequest richiesta) {
            runOnUiThread(() -> {
                boolean audio = false;
                for (String r : richiesta.getResources()) {
                    if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(r)) audio = true;
                }
                if (!audio) { richiesta.deny(); return; }
                if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                    richiesta.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
                } else {
                    if (richiestaMicrofono != null) richiestaMicrofono.deny();
                    richiestaMicrofono = richiesta;
                    requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, RICHIESTA_MICROFONO);
                }
            });
        }

        @Override
        public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams parametri) {
            if (sceltaFile != null) sceltaFile.onReceiveValue(null);
            sceltaFile = callback;
            Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.setType("*/*");
            try {
                startActivityForResult(Intent.createChooser(intent, "Scegli il manoscritto"), RICHIESTA_FILE);
            } catch (Exception e) {
                sceltaFile = null;
                callback.onReceiveValue(null);
                Toast.makeText(MainActivity.this, "Nessuna app disponibile per scegliere i file", Toast.LENGTH_LONG).show();
            }
            return true;
        }
    }

    @Override
    protected void onActivityResult(int codice, int risultato, Intent dati) {
        if (codice == RICHIESTA_FILE && sceltaFile != null) {
            sceltaFile.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(risultato, dati));
            sceltaFile = null;
            return;
        }
        super.onActivityResult(codice, risultato, dati);
    }

    @Override
    public void onRequestPermissionsResult(int codice, String[] permessi, int[] esiti) {
        if (codice != RICHIESTA_MICROFONO || richiestaMicrofono == null) return;
        if (esiti.length > 0 && esiti[0] == PackageManager.PERMISSION_GRANTED) {
            richiestaMicrofono.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
        } else {
            richiestaMicrofono.deny();
        }
        richiestaMicrofono = null;
    }

    /** Funzioni chiamate dalla pagina tramite window.AndroidApp. */
    private class Ponte {
        @JavascriptInterface
        public int ttsStato() { return statoTts; }

        @JavascriptInterface
        public void parla(String testo, String id, String nomeVoce) {
            if (statoTts == 2) { evento(id, "synthesis-failed"); return; }
            usaVoce(nomeVoce == null ? "" : nomeVoce);
            Bundle parametri = new Bundle();
            if (tts.speak(testo, TextToSpeech.QUEUE_ADD, parametri, id) != TextToSpeech.SUCCESS) {
                evento(id, "synthesis-failed");
            }
        }

        @JavascriptInterface
        public void ferma() { if (tts != null) tts.stop(); }

        /** Voci italiane installate, come JSON: [{"nome": "...", "rete": false}, ...]. */
        @JavascriptInterface
        public String voci() {
            JSONArray elenco = new JSONArray();
            try {
                if (statoTts < 0 || tts.getVoices() == null) return elenco.toString();
                for (Voice v : tts.getVoices()) {
                    if (!"it".equals(v.getLocale().getLanguage())) continue;
                    if (v.getFeatures() != null && v.getFeatures().contains(TextToSpeech.Engine.KEY_FEATURE_NOT_INSTALLED)) continue;
                    elenco.put(new JSONObject().put("nome", v.getName()).put("rete", v.isNetworkConnectionRequired()));
                }
            } catch (Exception ignorata) {}
            return elenco.toString();
        }

        /** Apre le impostazioni di sintesi vocale del telefono, dove si installano altre voci. */
        @JavascriptInterface
        public void apriImpostazioniVoce() {
            runOnUiThread(() -> {
                try {
                    startActivity(new Intent("com.android.settings.TTS_SETTINGS"));
                } catch (Exception e) {
                    try { startActivity(new Intent(android.provider.Settings.ACTION_SETTINGS)); } catch (Exception ignorata) {}
                }
            });
        }

        /** Salva un file in Download. Restituisce "" se va bene, altrimenti il messaggio d'errore. */
        @JavascriptInterface
        public String salvaFile(String base64, String nome, String tipo) {
            try {
                byte[] dati = Base64.decode(base64, Base64.DEFAULT);
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    ContentValues valori = new ContentValues();
                    valori.put(MediaStore.MediaColumns.DISPLAY_NAME, nome);
                    valori.put(MediaStore.MediaColumns.MIME_TYPE, tipo);
                    valori.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
                    Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, valori);
                    if (uri == null) return "Impossibile creare il file in Download.";
                    try (OutputStream out = getContentResolver().openOutputStream(uri)) {
                        if (out == null) return "Impossibile scrivere il file in Download.";
                        out.write(dati);
                    }
                } else {
                    File cartella = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
                    if (cartella == null) return "Memoria non disponibile.";
                    try (OutputStream out = new FileOutputStream(new File(cartella, nome))) {
                        out.write(dati);
                    }
                }
                runOnUiThread(() -> Toast.makeText(MainActivity.this, "Salvato in Download: " + nome, Toast.LENGTH_LONG).show());
                return "";
            } catch (Exception e) {
                return "Impossibile salvare il file: " + e.getMessage();
            }
        }
    }

    private void usaVoce(String nome) {
        if (nome.equals(voceAttuale)) return;
        voceAttuale = nome;
        if (nome.isEmpty()) { tts.setLanguage(Locale.ITALY); return; }
        try {
            for (Voice v : tts.getVoices()) {
                if (v.getName().equals(nome)) { tts.setVoice(v); return; }
            }
        } catch (Exception ignorata) {}
        tts.setLanguage(Locale.ITALY);
    }

    @Override
    protected void onSaveInstanceState(Bundle stato) {
        super.onSaveInstanceState(stato);
        webView.saveState(stato);
    }

    @Override
    protected void onDestroy() {
        if (tts != null) tts.shutdown();
        webView.destroy();
        super.onDestroy();
    }
}

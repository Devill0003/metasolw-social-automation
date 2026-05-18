package in.metasolw.statushelper;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.content.Intent;
import android.net.Uri;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.graphics.Color;

import androidx.core.content.FileProvider;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class MainActivity extends Activity {
    private static final String POSTER_URL =
            "https://raw.githubusercontent.com/Devill0003/metasolw-social-automation/main/public/status_today.png";

    private TextView statusText;
    private Button shareButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildUi();

        new Handler(Looper.getMainLooper()).postDelayed(new Runnable() {
            @Override
            public void run() {
                downloadAndShare();
            }
        }, 700);
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER);
        root.setPadding(42, 42, 42, 42);
        root.setBackgroundColor(Color.rgb(6, 26, 51));

        TextView title = new TextView(this);
        title.setText("MetaSolw Status Helper");
        title.setTextColor(Color.WHITE);
        title.setTextSize(26);
        title.setGravity(Gravity.CENTER);
        title.setPadding(0, 0, 0, 16);

        statusText = new TextView(this);
        statusText.setText("Latest poster download ho raha hai...");
        statusText.setTextColor(Color.rgb(230, 240, 255));
        statusText.setTextSize(16);
        statusText.setGravity(Gravity.CENTER);
        statusText.setPadding(0, 0, 0, 32);

        shareButton = new Button(this);
        shareButton.setText("Post WhatsApp Status Now");
        shareButton.setTextSize(16);
        shareButton.setAllCaps(false);
        shareButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                downloadAndShare();
            }
        });

        root.addView(title);
        root.addView(statusText);
        root.addView(shareButton);
        setContentView(root);
    }

    private void setStatus(final String text) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                statusText.setText(text);
            }
        });
    }

    private void downloadAndShare() {
        shareButton.setEnabled(false);
        setStatus("Poster download ho raha hai...");

        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    File output = new File(getCacheDir(), "metasolw_status_today.png");
                    downloadFile(POSTER_URL + "?cache=" + System.currentTimeMillis(), output);
                    setStatus("Poster ready. WhatsApp Status open ho raha hai...");
                    shareToWhatsAppStatus(output);
                } catch (Exception e) {
                    setStatus("Error: " + e.getMessage());
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            shareButton.setEnabled(true);
                        }
                    });
                }
            }
        }).start();
    }

    private void downloadFile(String link, File output) throws Exception {
        URL url = new URL(link);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setConnectTimeout(20000);
        conn.setReadTimeout(30000);
        conn.setInstanceFollowRedirects(true);
        conn.connect();

        int code = conn.getResponseCode();
        if (code < 200 || code >= 300) {
            throw new Exception("Download failed: HTTP " + code);
        }

        InputStream in = conn.getInputStream();
        FileOutputStream out = new FileOutputStream(output);

        byte[] buffer = new byte[8192];
        int read;
        while ((read = in.read(buffer)) != -1) {
            out.write(buffer, 0, read);
        }

        out.flush();
        out.close();
        in.close();
        conn.disconnect();
    }

    private void shareToWhatsAppStatus(File imageFile) {
        Uri uri = FileProvider.getUriForFile(
                this,
                getPackageName() + ".fileprovider",
                imageFile
        );

        if (tryShareToStatus(uri, "com.whatsapp.w4b")) {
            return;
        }

        if (tryShareToStatus(uri, "com.whatsapp")) {
            return;
        }

        openAndroidShareSheet(uri);
    }

    private boolean tryShareToStatus(Uri uri, String packageName) {
        try {
            grantUriPermission(packageName, uri, Intent.FLAG_GRANT_READ_URI_PERMISSION);

            Intent intent = new Intent("com.whatsapp.intent.action.SEND_TO_STATUS");
            intent.setType("image/png");
            intent.setPackage(packageName);
            intent.putExtra(Intent.EXTRA_STREAM, uri);

            // Direct WhatsApp Status target
            

            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            

            startActivity(intent);
            return true;
        } catch (Exception ignored) {
            return false;
        }
    }

    private void openAndroidShareSheet(Uri uri) {
        try {
            Intent send = new Intent(Intent.ACTION_SEND);
            send.setType("image/png");
            send.putExtra(Intent.EXTRA_STREAM, uri);
            send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            startActivity(Intent.createChooser(send, "Share MetaSolw Poster"));
        } catch (Exception e) {
            setStatus("WhatsApp open nahi hua: " + e.getMessage());
        }
    }
}
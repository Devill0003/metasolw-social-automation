package in.metasolw.statushelper;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Build;
import android.os.Environment;
import android.content.Intent;
import android.content.ContentValues;
import android.net.Uri;
import android.provider.MediaStore;
import android.media.MediaScannerConnection;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.graphics.Color;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.io.InputStream;
import java.io.ByteArrayOutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class MainActivity extends Activity {
    private static final String POSTER_URL =
            "https://raw.githubusercontent.com/Devill0003/metasolw-social-automation/main/public/status_today.png";

    private TextView statusText;
    private Button openButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildUi();

        new Handler(Looper.getMainLooper()).postDelayed(new Runnable() {
            @Override
            public void run() {
                downloadSaveAndOpenWhatsApp();
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
        statusText.setText("Poster download ho raha hai...");
        statusText.setTextColor(Color.rgb(230, 240, 255));
        statusText.setTextSize(16);
        statusText.setGravity(Gravity.CENTER);
        statusText.setPadding(0, 0, 0, 32);

        openButton = new Button(this);
        openButton.setText("Open WhatsApp Business");
        openButton.setTextSize(16);
        openButton.setAllCaps(false);
        openButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                downloadSaveAndOpenWhatsApp();
            }
        });

        root.addView(title);
        root.addView(statusText);
        root.addView(openButton);
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

    private void downloadSaveAndOpenWhatsApp() {
        openButton.setEnabled(false);
        setStatus("Latest poster download ho raha hai...");

        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    byte[] posterBytes = downloadBytes(POSTER_URL + "?cache=" + System.currentTimeMillis());
                    savePosterToGallery(posterBytes);
                    setStatus("Poster Gallery me save ho gaya. WhatsApp Business open ho raha hai...");
                    openFirstWhatsAppBusiness();
                } catch (Exception e) {
                    setStatus("Error: " + e.getMessage());
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            openButton.setEnabled(true);
                        }
                    });
                }
            }
        }).start();
    }

    private byte[] downloadBytes(String link) throws Exception {
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
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();

        byte[] data = new byte[8192];
        int read;
        while ((read = in.read(data)) != -1) {
            buffer.write(data, 0, read);
        }

        in.close();
        conn.disconnect();

        return buffer.toByteArray();
    }

    private void savePosterToGallery(byte[] bytes) throws Exception {
        String fileName = "MetaSolw_Status_" + System.currentTimeMillis() + ".png";

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ContentValues values = new ContentValues();
            values.put(MediaStore.Images.Media.DISPLAY_NAME, fileName);
            values.put(MediaStore.Images.Media.MIME_TYPE, "image/png");
            values.put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/MetaSolwStatus");
            values.put(MediaStore.Images.Media.IS_PENDING, 1);

            Uri uri = getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values);
            if (uri == null) {
                throw new Exception("Gallery save failed");
            }

            OutputStream out = getContentResolver().openOutputStream(uri);
            if (out == null) {
                throw new Exception("Gallery output failed");
            }

            out.write(bytes);
            out.flush();
            out.close();

            values.clear();
            values.put(MediaStore.Images.Media.IS_PENDING, 0);
            getContentResolver().update(uri, values, null, null);
        } else {
            File dir = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES), "MetaSolwStatus");
            if (!dir.exists()) {
                dir.mkdirs();
            }

            File file = new File(dir, fileName);
            FileOutputStream out = new FileOutputStream(file);
            out.write(bytes);
            out.flush();
            out.close();

            MediaScannerConnection.scanFile(this, new String[]{file.getAbsolutePath()}, new String[]{"image/png"}, null);
        }
    }

    private void openFirstWhatsAppBusiness() {
        try {
            Intent intent = getPackageManager().getLaunchIntentForPackage("com.whatsapp.w4b");

            if (intent == null) {
                setStatus("WhatsApp Business app nahi mila.");
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        openButton.setEnabled(true);
                    }
                });
                return;
            }

            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
            startActivity(intent);
        } catch (Exception e) {
            setStatus("WhatsApp Business open nahi hua: " + e.getMessage());
        }
    }
}
package com.example.clothes_finder;

import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.util.Base64;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TableLayout;
import android.widget.TextView;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;

public class searching extends AppCompatActivity {

    Handler handler;
    Button Btn_send;
    TableLayout table;
    TextView send_result;

    ImageView ImgViewSelected;
    ImageView ImgViewExtracted;
    ImageView ImgViewResult;
    ImageView ImfViewRecommend1;
    ImageView ImfViewRecommend2;
    ImageView ImfViewRecommend3;

    String base64_img;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_searching);

        ImgViewSelected = findViewById(R.id.img_View_select);
        ImgViewExtracted = findViewById(R.id.extract_image);
        ImgViewResult = findViewById(R.id.result_image);
        ImfViewRecommend1 = findViewById(R.id.reco_img1);
        ImfViewRecommend2 = findViewById(R.id.reco_img2);
        ImfViewRecommend3 = findViewById(R.id.reco_img3);

        Btn_send = findViewById(R.id.send_Image);
        Btn_send.setEnabled(false);

        table = findViewById(R.id.result_table);
        table.setVisibility(View.GONE);

        send_result = findViewById(R.id.textView3);
        send_result.setVisibility(View.GONE);

        handler = new Handler();
    }

    /** 사진 업로드 Click **/
    public void load_image(View view) {
        table.setVisibility(View.GONE);
        Intent intent = new Intent();
        intent.setType("image/*");
        intent.setAction(Intent.ACTION_GET_CONTENT);
        startActivityForResult(intent, 0);
    }

    /** 사진 전송 Click **/
    public void send_image(View view) {
        table.setVisibility(View.GONE);
        Btn_send.setEnabled(false);
        send_result.setText("Picture Send...");
        send_result.setVisibility(View.VISIBLE);

        http_con_utils.sendImg2Server(base64_img, handler, Btn_send, send_result, table,
                ImgViewExtracted, ImgViewResult, ImfViewRecommend1,
                ImfViewRecommend2, ImfViewRecommend3, this);
    }

    /** Img 를 Base 64 로 변경하는 함수 **/
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (resultCode != Activity.RESULT_OK) {
            return;
        }

        Uri data_uri = data.getData();
        ImgViewSelected.setImageURI(data_uri);

        try{
            // Image View 에 출력
            InputStream in = getContentResolver().openInputStream(data_uri);

            // Bitmap 변환
            Bitmap image = BitmapFactory.decodeStream(in);
            ImgViewSelected.setImageBitmap(image);
            in.close();

            // Bitmap -> Base64 Encoding
            ByteArrayOutputStream baos = new ByteArrayOutputStream();   //바이트 배열을 차례대로 읽어 들이기위한 ByteArrayOutputStream클래스 선언
            image.compress(Bitmap.CompressFormat.PNG, 70, baos);    //bitmap을 압축 (숫자 70은 70%로 압축한다는 뜻)
            byte[] bytes = baos.toByteArray();  //해당 bitmap을 byte배열로 바꿔준다.
            base64_img = Base64.encodeToString(bytes, Base64.DEFAULT);  //Base 64 방식으로byte 배열을 String으로 변환

        } catch (IOException ioe) {
            ioe.printStackTrace();
        }

        Btn_send.setEnabled(true);

    }
}
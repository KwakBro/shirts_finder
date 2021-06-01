package com.example.clothes_finder;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.os.Handler;
import android.view.View;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {

    Handler handler;

    TextView view_id;
    TextView view_passwd;

    GLOBAL_ITEMS state;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        handler = new Handler();

        view_id = findViewById(R.id.text_login_id);
        view_passwd = findViewById(R.id.text_login_password);

        state = ((GLOBAL_ITEMS)getApplicationContext());
    }


    public void login(View view) {
        String id = view_id.getText().toString();
        String passwd = view_passwd.getText().toString();

        http_con_utils.login_http(id, passwd, handler, getBaseContext(), this);

        state.setID(id);
    }
}
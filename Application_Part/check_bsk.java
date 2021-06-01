package com.example.clothes_finder;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.os.Handler;
import android.widget.TextView;

import java.util.ArrayList;

public class check_bsk extends AppCompatActivity {

    TextView title;

    GLOBAL_ITEMS state;
    Handler handler;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_check_bsk);

        state = ((GLOBAL_ITEMS)getApplicationContext());
        handler = new Handler();

        title = findViewById(R.id.textview_name_print_bsk);
        title.setText(String.format("%s 찜 목록", state.getID()));

        http_con_utils.bsk_check(state.getID(), getApplicationContext(), handler, this, this);
    }
}

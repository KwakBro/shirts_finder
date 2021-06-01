package com.example.clothes_finder;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;

public class main_screen extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_screen);
    }

    public void Btn_click_searching(View view) {
        Intent intent = new Intent(getApplicationContext(), searching.class);
        startActivity(intent);
    }

    public void Btn_click_check_bsk(View view) {
        Intent intent = new Intent(getApplicationContext(), check_bsk.class);
        startActivity(intent);
    }

    public void Btn_click_check_order(View view) {
        Intent intent = new Intent(getApplicationContext(), check_order.class);
        startActivity(intent);
    }
}
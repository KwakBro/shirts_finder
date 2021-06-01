package com.example.clothes_finder;

import androidx.appcompat.app.AppCompatActivity;

import android.media.Image;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Adapter;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.Spinner;
import android.widget.SpinnerAdapter;
import android.widget.TextView;

public class searching_item_detail extends AppCompatActivity {

    protected String Item;

    ImageView detail_image;
    TextView detail_text;

    TextView input_address;
    TextView input_numeric;

    Handler handler;

    GLOBAL_ITEMS state;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_searching_item_detail);

        Item = getIntent().getStringExtra("item");

        detail_image = findViewById(R.id.imageView_detail);
        detail_text = findViewById(R.id.textView_detail);

        input_address = findViewById(R.id.text_address);
        input_numeric = findViewById(R.id.text_numeric);

        handler = new Handler();
        http_con_utils.detail_page(Item, detail_image, detail_text, handler, this);

        state = ((GLOBAL_ITEMS)getApplicationContext());

    }


    public void Btn_click_buy(View view) {
        String address = input_address.getText().toString();
        int numeric = Integer.parseInt(input_numeric.getText().toString());

        http_con_utils.buy_function(state.getID(), Item, numeric, address, handler, this);
    }


    public void Btn_click_bsk(View view) {
        int numeric = Integer.parseInt(input_numeric.getText().toString());

        http_con_utils.bsk_function(state.getID(), Item, numeric, handler, this);
    }
}
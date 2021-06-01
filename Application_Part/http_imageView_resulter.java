package com.example.clothes_finder;

import android.content.Context;
import android.content.Intent;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Toast;

public class http_imageView_resulter implements View.OnClickListener{

    protected String Item;
    protected Handler main_handler;
    protected Context main_context;

    public http_imageView_resulter(String item, Handler main_handler, Context main_context){
        this.Item = item;
        this.main_handler = main_handler;
        this.main_context = main_context;
    }

    @Override
    public void onClick(View v) {
        main_handler.post(new Runnable() {
            @Override
            public void run() {

                Intent intent = new Intent(main_context, searching_item_detail.class);
                intent.putExtra("item", Item);
                main_context.startActivity(intent);

            }
        });
    };
}

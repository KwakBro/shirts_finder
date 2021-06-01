package com.example.clothes_finder;

import android.content.Context;
import android.os.Handler;
import android.util.AttributeSet;
import android.view.LayoutInflater;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.bumptech.glide.Glide;

public class check_sub_layout extends LinearLayout {

    public check_sub_layout(Context context, AttributeSet attrs, check_item sampleItem){
        super(context, attrs);
        init(context, sampleItem);
    }

    public check_sub_layout(Context context, check_item sampleItem){
        super(context);
        init(context, sampleItem);
    }

    public check_sub_layout(Context context, check_item_bsk sampleItem, Handler handler, Context parent){
        super(context);
        init(context, sampleItem, handler, parent);
    }

    /** init for order_check **/
    private void init(Context context, check_item sampleItem) {
        LayoutInflater inflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        inflater.inflate(R.layout.layout_sub_layout, this, true);

        ImageView img = (ImageView)findViewById(R.id.glide_imageview);
        TextView txt_detail = (TextView)findViewById(R.id.detail_order);

        String filename = "shirts-" + sampleItem.item_ID + ".jpg";
        String img_url = "http://182.217.108.150:49125/search/img_src/" + filename;

        String output_txt = "";

        output_txt += String.format("설명     :   %s", Integer.parseInt(sampleItem.item_name));
        output_txt += String.format("수량     :  %s\n", Integer.parseInt(sampleItem.item_num));
        output_txt += String.format("주소     :  %s", sampleItem.order_address);

        Glide.with(this)
                .load(img_url)
                .into(img);
        txt_detail.setText(output_txt);

    }

    /** init for Bsk_check **/
    private void init(Context context, check_item_bsk sampleItem, Handler handler, Context parent) {
        LayoutInflater inflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        inflater.inflate(R.layout.layout_sub_layout, this, true);

        ImageView img = (ImageView)findViewById(R.id.glide_imageview);
        TextView txt_detail = (TextView)findViewById(R.id.detail_order);

        String filename = "shirts-" + sampleItem.item_ID + ".jpg";
        String img_url = "http://182.217.108.150:49125/search/img_src/" + filename;

        String output_txt = "";

        output_txt += String.format("설명    :   %s", Integer.parseInt(sampleItem.item_name));

        Glide.with(this)
                .load(img_url)
                .into(img);

        img.setOnClickListener(new http_imageView_resulter(filename, handler, parent));

        txt_detail.setText(output_txt);

    }
}

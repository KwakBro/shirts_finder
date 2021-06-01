package com.example.clothes_finder;

import android.app.Activity;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TableLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.bumptech.glide.Glide;

import org.jetbrains.annotations.NotNull;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;


import java.io.IOException;
import java.util.ArrayList;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class http_con_utils {

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    public static void login_http(String ID, String Pwd, Handler main_th_handler,
                                  Context screen_context, Context main_context){

        /** Making JSON body and Send! **/
        JSONObject json_input = new JSONObject();

        try {
            json_input.put("ID", ID);
            json_input.put("Password", Pwd);
        } catch (JSONException e) {
            e.printStackTrace();
            return;
        }

        Log.d("TEST", ID);
        Log.d("TEST", Pwd);

        RequestBody requestBody = RequestBody.create(MediaType.parse("application/json; charset=utf-8"), json_input.toString());

        Request request = new Request.Builder()
                .url("http://182.217.108.150:49125/search/login/")
                .post(requestBody)
                .build();

        OkHttpClient client = new OkHttpClient();

        /** this is result Handling **/
        client.newCall(request).enqueue(new Callback() {

            /** if Response FAIL **/
            @Override
            public void onFailure(@NotNull Call call, @NotNull IOException e) {
                e.printStackTrace();
            }

            /** if Response SUCCESS **/
            @Override
            public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {
                // Make JSON set
                String data = response.body().string();

                JSONObject response_json = null;
                boolean validate = false;

                try {
                    response_json = new JSONObject(data);
                    validate = response_json.getBoolean("valid");
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                // act for login success flag
                if (validate) {
                    main_th_handler.post(new Runnable() {
                        @Override
                        public void run() {
                            Toast.makeText(screen_context, String.format("Hello! %s", ID), Toast.LENGTH_LONG).show();

                            Intent intent = new Intent(main_context, main_screen.class);
                            main_context.startActivity(intent);

                        }
                    });

                    Log.d("TEST / RECEIVE  ", "Success" );
                }
                // act for login fail flag
                else{
                    main_th_handler.post(new Runnable() {
                        @Override
                        public void run() {
                            Toast.makeText(screen_context, String.format("Login FAIL!"), Toast.LENGTH_LONG).show();
                        }
                    });

                    Log.d("TEST / RECEIVE  ", "FAIL" );
                }

            }
        });
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    public static void sendImg2Server(String base64_img, Handler handler, Button Btn_send, TextView send_result, TableLayout table,
                                      ImageView extract, ImageView result, ImageView recommend1, ImageView recommend2, ImageView recommend3, Context parent) {

        /** Making JSON body and Send! **/
        JSONObject json_input = new JSONObject();

        try {
            json_input.put("img_base64", base64_img);
        } catch (JSONException e) {
            e.printStackTrace();
            return;
        }

        RequestBody requestBody = RequestBody.create(MediaType.parse("application/json; charset=utf-8"), json_input.toString());

        Request request = new Request.Builder()
                .url("http://182.217.108.150:49125/search/")
                .post(requestBody)
                .build();

        OkHttpClient client = new OkHttpClient();

        /** this is result Handling **/
        client.newCall(request).enqueue(new Callback() {

            /** if Response FAIL **/
            @Override
            public void onFailure(@NotNull Call call, @NotNull IOException e) {
                Log.d("TEST : ", "FAIL ");
                Log.d("TEST : ", e.toString());

                /** in FAIL Case **/
                handler.post(new Runnable() {
                    @Override
                    public void run() {
                        Btn_send.setEnabled(true);
                        send_result.setText("Response Failed!\n\n" + e.toString());
                    }
                });

            }

            /** if Response SUCCESS **/
            @Override
            public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {
                try {
                    // Response 받아서 저장
                    String data = response.body().string();
                    Log.d("TEST / RECEIVE  ", data);

                    // Response --> JSON parsing
                    JSONObject response_json = new JSONObject(data);

                    // FLAG check
                    int flag = response_json.getInt("FLAG");
                    Log.d("TEST / FLAG ", response_json.getString("FLAG"));

                    switch (flag) {

                        // TODO : 옷 사진이 아닌 경우
                        case 0:
                            handler.post(new Runnable() {
                                @Override
                                public void run() {
                                    Btn_send.setEnabled(true);
                                    send_result.setText("옷 검출 실패\n제대로 된 사진인지 확인해주세요");
                                }
                            });
                            break;

                        // TODO : 옷 사진일 경우, Matching Item 있는경우
                        case 1:

                            // Extracted Item 링크
                            String ex_ID = response_json.getString("request_ID");
                            String link_ex_1 = "http://182.217.108.150:49125/search/id_result/" + ex_ID.trim();

                            // Search Item 링크
                            String se_ID = response_json.getString("result");
                            String link_se_1 = "http://182.217.108.150:49125/search/img_src/" + se_ID.trim();

                            // 추천 아이템 링크
                            String[] temp = response_json.getString("recommand").replaceAll("[\\[\\]\"]", " ").trim().split(",");
                            String link_rec_1 = "http://182.217.108.150:49125/search/img_src/" + temp[0].trim();
                            String link_rec_2 = "http://182.217.108.150:49125/search/img_src/" + temp[1].trim();
                            String link_rec_3 = "http://182.217.108.150:49125/search/img_src/" + temp[2].trim();

                            handler.post(new Runnable() {
                                @Override
                                public void run() {

                                    Btn_send.setEnabled(true);
                                    send_result.setText("successfully completed!\nFind Matched Item");

                                    Glide.with(parent).load(link_ex_1).into(extract);
                                    Glide.with(parent).load(link_se_1).into(result);
                                    Glide.with(parent).load(link_rec_1).into(recommend1);
                                    Glide.with(parent).load(link_rec_2).into(recommend2);
                                    Glide.with(parent).load(link_rec_3).into(recommend3);

                                    result.setOnClickListener(new http_imageView_resulter(se_ID, handler, parent));
                                    recommend1.setOnClickListener(new http_imageView_resulter(temp[0].trim(), handler, parent));
                                    recommend2.setOnClickListener(new http_imageView_resulter(temp[1].trim(), handler, parent));
                                    recommend3.setOnClickListener(new http_imageView_resulter(temp[2].trim(), handler, parent));

                                    table.setVisibility(View.VISIBLE);

                                }
                            });
                            break;

                        // TODO : 옷 사진일 경우, Matching Item 없는경우
                        case 2:
                            // Extracted Item 링크
                            String case2_ex_ID = response_json.getString("request_ID");
                            String case2_link_ex_1 = "http://182.217.108.150:49125/search/id_result/" + case2_ex_ID.trim();

                            // 추천 아이템 링크
                            String[] case2_temp = response_json.getString("recommand").replaceAll("[\\[\\]\"]", " ").trim().split(",");
                            String case2_link_rec_1 = "http://182.217.108.150:49125/search/img_src/" + case2_temp[0].trim();
                            String case2_link_rec_2 = "http://182.217.108.150:49125/search/img_src/" + case2_temp[1].trim();
                            String case2_link_rec_3 = "http://182.217.108.150:49125/search/img_src/" + case2_temp[2].trim();

                            handler.post(new Runnable() {
                                @Override
                                public void run() {
                                    Btn_send.setEnabled(true);
                                    send_result.setText("successfully completed!");

                                    Glide.with(parent).load(case2_link_ex_1).into(extract);
                                    result.setImageResource(R.drawable.item_not_found);
                                    Glide.with(parent).load(case2_link_rec_1).into(recommend1);
                                    Glide.with(parent).load(case2_link_rec_2).into(recommend2);
                                    Glide.with(parent).load(case2_link_rec_3).into(recommend3);

                                    recommend1.setOnClickListener(new http_imageView_resulter(case2_temp[0].trim(), handler, parent));
                                    recommend2.setOnClickListener(new http_imageView_resulter(case2_temp[1].trim(), handler, parent));
                                    recommend3.setOnClickListener(new http_imageView_resulter(case2_temp[2].trim(), handler, parent));

                                    table.setVisibility(View.VISIBLE);
                                }
                            });
                            break;
                    }


                } catch (JSONException je) {
                    Log.d("TEST : ", je.toString());
                }

            }
        });
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    public static void detail_page(String item, ImageView img_view, TextView txt_view, Handler main_handler, Context parent){

        JSONObject json_input = new JSONObject();

        try {
            json_input.put("item", item);
        } catch (JSONException e) {
            e.printStackTrace();
            return;
        }

        RequestBody requestBody = RequestBody.create(MediaType.parse("application/json; charset=utf-8"), json_input.toString());

        Request request = new Request.Builder()
                .url("http://182.217.108.150:49125/search/db_query/item")
                .post(requestBody)
                .build();

        OkHttpClient client = new OkHttpClient();

        String img_url = "http://182.217.108.150:49125/search/img_src/" + item;

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NotNull Call call, @NotNull IOException e) {
                Log.d("TEST // FAIL ", e.toString());
            }

            @Override
            public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {

                // Response 받아서 저장
                String data = response.body().string();
                Log.d("TEST / RECEIVE  ", data);

                // Response --> JSON parsing
                JSONObject response_json = null;
                String detail_text = null;
                int detail_price = 0;

                try {
                    response_json = new JSONObject(data);
                    detail_text = response_json.getString("item_name");
                    detail_price = response_json.getInt("item_price");
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                String finalDetail_text = detail_text;
                int finalDetail_price = detail_price;

                main_handler.post(new Runnable() {
                    @Override
                    public void run() {

                        Glide.with(parent).load(img_url).into(img_view);

                        txt_view.setText( String.format("상품 설명  :  %s\n상품 가격  :  %d", finalDetail_text, finalDetail_price) );

                    }
                });


            }
        });

    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    public static void buy_function(String ID, String item, int num, String address, Handler main_handler, Activity parent){
        JSONObject json_input = new JSONObject();

        try {
            json_input.put("ID", ID);
            json_input.put("item", item);
            json_input.put("num", num);
            json_input.put("address", address);
        } catch (JSONException e) {
            e.printStackTrace();
            return;
        }

        RequestBody requestBody = RequestBody.create(MediaType.parse("application/json; charset=utf-8"), json_input.toString());

        Request request = new Request.Builder()
                .url("http://182.217.108.150:49125/search/db_query/order")
                .post(requestBody)
                .build();

        OkHttpClient client = new OkHttpClient();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NotNull Call call, @NotNull IOException e) {
                Log.d("TEST // FAIL ", e.toString());
            }

            @Override
            public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {

                // Response 받아서 저장
                String data = response.body().string();
                Log.d("TEST / RECEIVE  ", data);

                // Response --> JSON parsing
                JSONObject response_json = null;
                boolean flag = false;

                try {
                    response_json = new JSONObject(data);
                    flag = response_json.getBoolean("flag");
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                main_handler.post(new Runnable() {
                    @Override
                    public void run() {
                        parent.finish();
                    }
                });


            }
        });

    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    public static void bsk_function(String ID, String item, int num, Handler main_handler, Activity parent){
        JSONObject json_input = new JSONObject();

        try {
            json_input.put("ID", ID);
            json_input.put("item", item);
            json_input.put("num", num);
        } catch (JSONException e) {
            e.printStackTrace();
            return;
        }

        RequestBody requestBody = RequestBody.create(MediaType.parse("application/json; charset=utf-8"), json_input.toString());

        Request request = new Request.Builder()
                .url("http://182.217.108.150:49125/search/db_query/bsk")
                .post(requestBody)
                .build();

        OkHttpClient client = new OkHttpClient();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NotNull Call call, @NotNull IOException e) {
                Log.d("TEST // FAIL ", e.toString());
            }

            @Override
            public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {

                // Response 받아서 저장
                String data = response.body().string();
                Log.d("TEST / RECEIVE  ", data);

                // Response --> JSON parsing
                JSONObject response_json = null;
                boolean flag = false;

                try {
                    response_json = new JSONObject(data);
                    flag = response_json.getBoolean("flag");
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                main_handler.post(new Runnable() {
                    @Override
                    public void run() {
                        parent.finish();
                    }
                });

            }
        });

    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    public static void order_check(String ID, Context main_context, Handler main_handler, Activity parent){
        JSONObject json_input = new JSONObject();

        try {
            json_input.put("ID", ID);
        } catch (JSONException e) {
            e.printStackTrace();
            return;
        }

        RequestBody requestBody = RequestBody.create(MediaType.parse("application/json; charset=utf-8"), json_input.toString());

        Request request = new Request.Builder()
                .url("http://182.217.108.150:49125/search/db_query/checkorder")
                .post(requestBody)
                .build();

        OkHttpClient client = new OkHttpClient();
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NotNull Call call, @NotNull IOException e) {
                Log.d("TEST", e.toString());
            }

            @Override
            public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {
                // Response 받아서 저장
                String data = response.body().string();
                Log.d("TEST / RECEIVE  ", data);

                // Response --> JSON parsing
                JSONObject response_json = null;
                JSONArray items = null;

                try {
                    response_json = new JSONObject(data);
                    items = response_json.getJSONArray("item");
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                // Activity 생성 위함.
                ArrayList<check_item> arrayList;
                arrayList = new ArrayList<>();

                for (int idx = 0; idx < items.length() ; idx++){

                    JSONObject item;

                    try {

                        item = items.getJSONObject(idx);

                        String item_ID = item.getString("item_ID");
                        String item_num = item.getString("item_num");
                        String item_name = item.getString("item_name");
                        String order_address = item.getString("order_address");

                        check_item SubItem = new check_item(item_ID, item_name, item_num, order_address);
                        arrayList.add(SubItem);

                    } catch (JSONException e) {
                        e.printStackTrace();
                    }

                }

                main_handler.post(new Runnable() {
                    @Override
                    public void run() {
                        for ( int idx = 0; idx < arrayList.size(); idx++){
                            check_sub_layout sub_layout = new check_sub_layout(main_context, arrayList.get(idx));
                            LinearLayout layout = (LinearLayout)parent.findViewById(R.id.input_order_layout);
                            layout.addView(sub_layout);
                        }

                    }
                });


            }
        });

    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    public static void bsk_check(String ID, Context main_context, Handler main_handler, Activity parent, Context parent_context){
        JSONObject json_input = new JSONObject();

        try {
            json_input.put("ID", ID);
        } catch (JSONException e) {
            e.printStackTrace();
            return;
        }

        RequestBody requestBody = RequestBody.create(MediaType.parse("application/json; charset=utf-8"), json_input.toString());

        Request request = new Request.Builder()
                .url("http://182.217.108.150:49125/search/db_query/checkbsk")
                .post(requestBody)
                .build();

        OkHttpClient client = new OkHttpClient();
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NotNull Call call, @NotNull IOException e) {
                Log.d("TEST", e.toString());
            }

            @Override
            public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {
                // Response 받아서 저장
                String data = response.body().string();
                Log.d("TEST / RECEIVE  ", data);

                // Response --> JSON parsing
                JSONObject response_json = null;
                JSONArray items = null;

                try {
                    response_json = new JSONObject(data);
                    items = response_json.getJSONArray("item");
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                // Activity 생성 위함.
                ArrayList<check_item_bsk> arrayList;
                arrayList = new ArrayList<>();

                for (int idx = 0; idx < items.length() ; idx++){

                    JSONObject item;

                    try {

                        item = items.getJSONObject(idx);

                        String item_ID = item.getString("item_ID");
                        String item_name = item.getString("item_name");

                        check_item_bsk SubItem = new check_item_bsk(item_ID, item_name);
                        arrayList.add(SubItem);

                    } catch (JSONException e) {
                        e.printStackTrace();
                    }

                }

                main_handler.post(new Runnable() {
                    @Override
                    public void run() {
                        for ( int idx = 0; idx < arrayList.size(); idx++){
                            check_sub_layout sub_layout = new check_sub_layout(main_context, arrayList.get(idx), main_handler, parent_context);
                            LinearLayout layout = (LinearLayout)parent.findViewById(R.id.input_bsk_layout);
                            layout.addView(sub_layout);
                        }

                        // Image View 추가

                    }
                });


            }
        });

    }
}

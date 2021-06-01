package com.example.clothes_finder;

import android.app.Application;

public class GLOBAL_ITEMS extends Application {
    private String ID;

    public String getID(){
        return ID;
    }
    public void setID(String ID){
        this.ID = ID;
    }
}

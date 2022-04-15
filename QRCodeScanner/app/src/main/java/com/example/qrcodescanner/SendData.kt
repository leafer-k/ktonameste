package com.example.qrcodescanner

import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.annotation.WorkerThread
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.lang.Exception
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.*

private const val ENDPOINT = "https://leafer.pythonanywhere.com/attendanceRequest"
private const val CODE = "code"
private const val DATE = "date"
private const val TIME = "time"

class SendData : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val code = intent.getStringExtra("code")
        Log.d("INTENT", "INTENT EXTRA: $code")

        try {
            if (code != null) {
                Thread {
                    addCode(code)
                }.start()
            } else {
                Toast.makeText(applicationContext, "Wrong code", Toast.LENGTH_SHORT).show()
            }
        }
        catch (exception : Exception){
            Toast.makeText(applicationContext, "Wrong QR", Toast.LENGTH_SHORT).show()
        }

        finish()
    }

    @WorkerThread
    fun addCode(intentCode: String) {
        val sdf = SimpleDateFormat("dd.MM.yyyy")
        val stf = SimpleDateFormat("HH:mm")

        val currentDate = sdf.format(Date())
        val currentTime = stf.format(Date())


        val httpUrlConnection = URL(ENDPOINT).openConnection() as HttpURLConnection
        val body = JSONObject().apply {
            put(DATE, currentDate)
            put(TIME, currentTime)
            put(CODE, intentCode)
        }

        httpUrlConnection.apply {
            connectTimeout = 10000
            requestMethod = "POST"
            doOutput = true
            setRequestProperty("Content-Type", "application/json")
        }

        Log.d("JSON", body.toString())

        OutputStreamWriter(httpUrlConnection.outputStream).use {
            it.write(body.toString())
        }
        Log.d("HTTP", httpUrlConnection.responseMessage)
        httpUrlConnection.disconnect()
    }

}
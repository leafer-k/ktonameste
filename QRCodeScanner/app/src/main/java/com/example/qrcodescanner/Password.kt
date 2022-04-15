package com.example.qrcodescanner

import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.annotation.WorkerThread
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

private const val ENDPOINT = "https://leafer.pythonanywhere.com/scanner_login"

class Password : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_password)

        val okButton: Button = findViewById(R.id.button)
        val passET : EditText = findViewById(R.id.editTextPassword)
        val loginET : EditText = findViewById(R.id.editTextLogin)
        val mainIntent = Intent(this, MainActivity::class.java)
        var loginResponse: Int = 0

        okButton.setOnClickListener {
            Thread {
                loginResponse = webLogin(password = passET.text.toString(), login = loginET.text.toString())

                if (loginResponse == 202){
                    startActivity(mainIntent)
                    finish()
                }
                else if (loginResponse == 406){
                    Log.d("HTTP", "Неверный логин или пароль!")
                }
                else{
                    Log.d("HTTP", "Ошибка!")
                }
            }.start()

            Log.d("JSON", loginResponse.toString())


        }

    }

    @WorkerThread
    fun webLogin(password: String, login: String) : Int{
        val httpUrlConnection = URL(ENDPOINT).openConnection() as HttpURLConnection
        val body = JSONObject().apply {
            put("login", login)
            put("password", password)
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
        Log.d("HTTP", httpUrlConnection.responseCode.toString())
        httpUrlConnection.disconnect()
        return httpUrlConnection.responseCode
    }

}
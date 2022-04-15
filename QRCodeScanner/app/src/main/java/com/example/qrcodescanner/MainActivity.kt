package com.example.qrcodescanner

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.os.IInterface
import android.os.PersistableBundle
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import com.google.zxing.integration.android.IntentIntegrator
import com.google.zxing.integration.android.IntentResult

class MainActivity : AppCompatActivity() {

    override fun onStart() {
        super.onStart()
        setContentView(R.layout.activity_main)

        val scanButton: Button = findViewById(R.id.scanButton)

        scanButton.setOnClickListener {
            val intentIntegrator: IntentIntegrator = IntentIntegrator(
                this@MainActivity
            )
            intentIntegrator.setPrompt(
                "Для включения фонарика используйте кнопку увеличения громкости"
            )
            intentIntegrator.setOrientationLocked(true)
            intentIntegrator.captureActivity = Capture::class.java
            intentIntegrator.initiateScan()
        }

    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        val intentResult: IntentResult = IntentIntegrator.parseActivityResult(
            requestCode, resultCode, data
        )

        if(intentResult.contents != null){
            val sendIntent = Intent(this, SendData::class.java)
            sendIntent.putExtra("code", intentResult.contents)
            startActivity(sendIntent)

            val builder : AlertDialog.Builder = AlertDialog.Builder(
                this@MainActivity
            )
            builder.setTitle("Result")
            builder.setMessage(intentResult.contents)
            builder.setPositiveButton(
                "OK"
            ) { dialog, i -> dialog.dismiss() }
            builder.show()
        } else {
            Toast.makeText(applicationContext, "Not found", Toast.LENGTH_SHORT).show()
        }
    }
}
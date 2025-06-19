package com.aquaa.alphamath;

import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast; // Added for user feedback

import androidx.appcompat.app.AppCompatActivity;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class ProjActivity extends AppCompatActivity {

    EditText inputField;
    Button expandButton, simplifyButton, factoriseButton, substituteButton;
    TextView outputView;

    // Name of your Python script (e.g., proj.py, make sure it's in src/main/python)
    private final String PYTHON_MODULE_NAME = "proj"; // Changed from "Proj" to "proj" to match typical Python naming

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_proj);

        // Initialize Python if not already started
        // This is crucial if ProjActivity can be launched independently
        // or if MainActivity might not have started it yet.
        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }

        inputField = findViewById(R.id.inputField);
        expandButton = findViewById(R.id.expandButton);
        simplifyButton = findViewById(R.id.simplifyButton);
        factoriseButton = findViewById(R.id.factoriseButton);   // New
        substituteButton = findViewById(R.id.substituteButton); // New
        outputView = findViewById(R.id.outputView);

        // Basic null checks for UI elements (good practice)
        if (inputField == null || expandButton == null || simplifyButton == null ||
                factoriseButton == null || substituteButton == null || outputView == null) {
            Toast.makeText(this, "Error initializing UI components.", Toast.LENGTH_LONG).show();
            // Potentially disable buttons or finish activity if UI is broken
            return;
        }


        expandButton.setOnClickListener(v -> {
            String expression = inputField.getText().toString().trim();
            if (expression.isEmpty()) {
                outputView.setText("❌ Error: Expression cannot be empty.");
                return;
            }
            runPythonScript(expression, "expand");
        });

        simplifyButton.setOnClickListener(v -> {
            String expression = inputField.getText().toString().trim();
            if (expression.isEmpty()) {
                outputView.setText("❌ Error: Expression cannot be empty.");
                return;
            }
            runPythonScript(expression, "simplify");
        });

        factoriseButton.setOnClickListener(v -> { // New
            String expression = inputField.getText().toString().trim();
            if (expression.isEmpty()) {
                outputView.setText("❌ Error: Expression cannot be empty.");
                return;
            }
            runPythonScript(expression, "factor"); // "factor" as mode
        });

        substituteButton.setOnClickListener(v -> { // New
            String fullInput = inputField.getText().toString().trim();
            if (fullInput.isEmpty()) {
                outputView.setText("❌ Error: Input cannot be empty.");
                return;
            }
            // For substitute, the input is passed as is.
            // The Python script will handle parsing the expression and variables.
            runPythonScript(fullInput, "substitute");
        });
    }

    private void runPythonScript(String argument, String mode) {
        outputView.setText("Processing..."); // Provide immediate feedback

        new Thread(() -> {
            try {
                Python py = Python.getInstance();
                PyObject module = py.getModule(PYTHON_MODULE_NAME);

                if (module == null) {
                    runOnUiThread(() -> outputView.setText("❌ Error: Python module '" + PYTHON_MODULE_NAME + "' not found."));
                    return;
                }
                if (!module.containsKey("main")) {
                    runOnUiThread(() -> outputView.setText("❌ Error: 'main' function not found in Python module."));
                    return;
                }

                // Call the 'main' function in Python with the expression and the mode
                PyObject result = module.callAttr("main", argument, mode);

                String output = result != null ? result.toString() : "No output from script.";
                runOnUiThread(() -> outputView.setText(output));

            } catch (Exception e) {
                // It's good to log the full exception for debugging
                e.printStackTrace(); // This will print to Logcat
                String errorMessage = "❌ Error processing script: " + e.getMessage();
                // For PyException, the message might already be user-friendly from your Python script
                if (e instanceof com.chaquo.python.PyException) {
                    errorMessage = e.getMessage(); // Use the message directly if it's from Python
                }
                final String finalErrorMessage = errorMessage;
                runOnUiThread(() -> outputView.setText(finalErrorMessage));
            }
        }).start();
    }
}
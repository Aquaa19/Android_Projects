package com.aquaa.alphamath;

import android.content.Intent;
import android.graphics.Rect;
import android.os.Bundle;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Button;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class MainActivity extends AppCompatActivity {

    TextView outputTextView;
    EditText inputEditText;
    Button submitInputButton;
    TextView moduleInfoTextView;
    TextView inputHintTextView;
    Spinner moduleSpinner;

    private String activePythonModule = null;

    private ActivityResultLauncher<Intent> projActivityLauncher;

    private final String[] moduleLabels = {
            "Select Module", "Congruence", "CRT", "Cubic", "Multiplier",
            "PolyDiv", "Trigonometric Calculator", "Quadratic Solver", "Sturm Sequence",
            "Project Activity"
    };

    private final String[] moduleValues = {
            null, "congruence", "CRT", "cubic", "multiplier",
            "Poly_long_div", "trig_calc", "Quad", "sturm_final",
            "PROJ_ACTIVITY"
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        outputTextView = findViewById(R.id.outputTextView);
        inputEditText = findViewById(R.id.inputEditText);
        submitInputButton = findViewById(R.id.submitInputButton);
        moduleInfoTextView = findViewById(R.id.moduleInfoTextView);
        inputHintTextView = findViewById(R.id.inputHintTextView);
        moduleSpinner = findViewById(R.id.moduleSpinner);

        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }

        resetToInitialState();

        ArrayAdapter<String> adapter = new ArrayAdapter<>(this,
                android.R.layout.simple_spinner_item, moduleLabels);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        moduleSpinner.setAdapter(adapter);

        projActivityLauncher = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                result -> {
                    moduleSpinner.setSelection(0);
                    resetToInitialState();
                });

        moduleSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int pos, long id) {
                String selectedValue = moduleValues[pos];

                if (selectedValue == null) {
                    resetToInitialState();
                    return;
                }

                if (selectedValue.equals("PROJ_ACTIVITY")) {
                    activePythonModule = null;
                    Intent intent = new Intent(MainActivity.this, ProjActivity.class);
                    projActivityLauncher.launch(intent);

                    moduleInfoTextView.setText("Project Activity is open...");
                    inputHintTextView.setText("Close Project Activity to select another module.");
                    inputEditText.setVisibility(View.GONE);
                    submitInputButton.setVisibility(View.GONE);
                    outputTextView.setVisibility(View.GONE);
                } else {
                    inputEditText.setVisibility(View.VISIBLE);
                    submitInputButton.setVisibility(View.VISIBLE);
                    outputTextView.setVisibility(View.VISIBLE);
                    setActivePythonModule(selectedValue, getHintForModule(selectedValue));
                }
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
                resetToInitialState();
            }
        });

        final View rootView = findViewById(android.R.id.content);
        rootView.getViewTreeObserver().addOnGlobalLayoutListener(() -> {
            Rect r = new Rect();
            rootView.getWindowVisibleDisplayFrame(r);
            int screenHeight = rootView.getRootView().getHeight();
            int keypadHeight = screenHeight - r.bottom;

            if (activePythonModule != null && inputEditText.getVisibility() == View.VISIBLE) {
                if (keypadHeight > screenHeight * 0.15) {
                    submitInputButton.setVisibility(View.GONE);
                } else {
                    submitInputButton.setVisibility(View.VISIBLE);
                }
            } else {
                if (activePythonModule == null) {
                    submitInputButton.setVisibility(View.GONE);
                }
            }
        });

        submitInputButton.setOnClickListener(v -> {
            String input = inputEditText.getText().toString().trim();

            if (activePythonModule == null) {
                Toast.makeText(this, getString(R.string.hint_select_module), Toast.LENGTH_SHORT).show();
                return;
            }

            if (argumentRequiredForModule(activePythonModule) && input.isEmpty()) {
                Toast.makeText(this, "Input is required for " + activePythonModule, Toast.LENGTH_SHORT).show();
                outputTextView.setText("Error: Input is required for " + activePythonModule + ".\nFormat: " + getHintForModule(activePythonModule));
                return;
            }

            runActivePythonModule(input);
        });

        inputEditText.setOnEditorActionListener((textView, actionId, event) -> {
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                if (activePythonModule != null && submitInputButton.getVisibility() == View.VISIBLE) {
                    submitInputButton.performClick();
                    return true;
                }
            }
            return false;
        });
    }

    private void resetToInitialState() {
        activePythonModule = null;
        moduleInfoTextView.setText(getString(R.string.hint_select_module));
        inputHintTextView.setText(getString(R.string.hint_guide_initial));
        outputTextView.setText("");
        inputEditText.setText("");
        inputEditText.setVisibility(View.GONE);
        submitInputButton.setVisibility(View.GONE);
        outputTextView.setVisibility(View.GONE);
    }

    private void setActivePythonModule(String moduleName, String hintText) {
        if (activePythonModule == null || !activePythonModule.equals(moduleName)) {
            inputEditText.setText("");
        }
        activePythonModule = moduleName;

        moduleInfoTextView.setText(getString(R.string.module_selected_info, moduleName));
        inputHintTextView.setText(hintText);

        outputTextView.setText(getString(R.string.processing_message, activePythonModule));

        inputEditText.setHint(getString(R.string.hint_enter_input_generic));
        inputEditText.requestFocus();

        Toast.makeText(this, getString(R.string.module_selected_toast, moduleName), Toast.LENGTH_SHORT).show();
    }

    private void runActivePythonModule(String argument) {
        if (activePythonModule == null) {
            Toast.makeText(this, getString(R.string.hint_select_module), Toast.LENGTH_SHORT).show();
            return;
        }

        outputTextView.setText(getString(R.string.processing_message, activePythonModule));

        new Thread(() -> {
            try {
                Python py = Python.getInstance();
                PyObject module = py.getModule(activePythonModule);

                if (module == null) {
                    runOnUiThread(() -> outputTextView.setText("Error: Python module '" + activePythonModule + "' not found."));
                    return;
                }

                if (!module.containsKey("main")) {
                    runOnUiThread(() -> outputTextView.setText("Error: Python module '" + activePythonModule + "' does not have a main() function."));
                    return;
                }

                PyObject result;
                if (!argumentRequiredForModule(activePythonModule) && (argument == null || argument.isEmpty())) {
                    result = module.callAttr("main");
                } else {
                    result = module.callAttr("main", argument);
                }

                final String output = result != null ? result.toString() : "No result returned from " + activePythonModule + ".";
                runOnUiThread(() ->
                {
                    outputTextView.setText(output);
                    outputTextView.setHorizontallyScrolling(true);
                    outputTextView.setTextIsSelectable(true);
                });

            } catch (Exception e) {
                final String errMsg = "Error processing with " + activePythonModule + ":\n" + e.getMessage();
                runOnUiThread(() -> outputTextView.setText(errMsg));
                e.printStackTrace();
            }
        }).start();
    }

    private boolean argumentRequiredForModule(String moduleName) {
        if (moduleName == null || moduleName.equals("PROJ_ACTIVITY")) return false;
        return !moduleName.equals("sturm_final");
    }

    private String getHintForModule(String moduleName) {
        if (moduleName == null) return getString(R.string.hint_guide_initial);
        switch (moduleName) {
            case "congruence":
                return getString(R.string.hint_congruence);
            case "CRT":
                return getString(R.string.hint_crt);
            case "cubic":
                return getString(R.string.hint_cubic);
            case "multiplier":
                return getString(R.string.hint_multiplier);
            case "Poly_long_div":
                return getString(R.string.hint_poly_long_div);
            case "trig_calc":
                return getString(R.string.hint_trig_calc);
            case "Quad":
                return getString(R.string.hint_quad);
            case "sturm_final":
                return getString(R.string.hint_sturm_final);
            default:
                return getString(R.string.hint_guide_initial);
        }
    }

    public void exitApp(View view) {
        finishAffinity();
    }
}
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::api::process::{Command, CommandEvent};
use tauri::Manager;

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn run_ocr_process(pdf_path: String, output_folder: String, no_csv: bool) -> Result<String, String> {
    let (mut rx, child) = Command::new("python")
        .args(&[
            "src/ocr_poc.py",
            &pdf_path,
            "--output_folder", &output_folder,
            if no_csv { "--no-csv" } else { "" }
        ])
        .spawn()
        .map_err(|e| format!("Failed to spawn python process: {}", e))?;

    let mut output = String::new();
    while let Some(event) = rx.recv().await {
        match event {
            CommandEvent::Stdout(line) => {
                output.push_str(&line);
                output.push_str("\n");
            },
            CommandEvent::Stderr(line) => {
                output.push_str(&format!("ERROR: {}\n", line));
            },
            _ => {}
        }
    }

    let status = child.wait().await.map_err(|e| format!("Failed to wait for python process: {}", e))?;

    if status.success() {
        Ok(output)
    } else {
        Err(format!("Python process exited with error: {}\n{}", status, output))
    }
}

#[tauri::command]
async fn run_accuracy_review(ocr_csv_path: String, ground_truth_json_path: String, iou_threshold: f64) -> Result<String, String> {
    let (mut rx, child) = Command::new("python")
        .args(&[
            "scripts/accuracy_reviewer.py",
            "--ocr_csv", &ocr_csv_path,
            "--ground_truth_json", &ground_truth_json_path,
            "--iou_threshold", &iou_threshold.to_string()
        ])
        .spawn()
        .map_err(|e| format!("Failed to spawn python process: {}", e))?;

    let mut output = String::new();
    while let Some(event) = rx.recv().await {
        match event {
            CommandEvent::Stdout(line) => {
                output.push_str(&line);
                output.push_str("\n");
            },
            CommandEvent::Stderr(line) => {
                output.push_str(&format!("ERROR: {}\n", line));
            },
            _ => {}
        }
    }

    let status = child.wait().await.map_err(|e| format!("Failed to wait for python process: {}", e))?;

    if status.success() {
        Ok(output)
    } else {
        Err(format!("Python process exited with error: {}\n{}", status, output))
    }
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet, run_ocr_process, run_accuracy_review])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

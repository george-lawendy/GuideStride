# GuideStride

GuideStride is an AI-powered wearable running guidance system designed to detect a runner's lateral drift and provide real-time directional haptic feedback.

## Overview

The system combines computer vision and IMU sensing to classify runner movement into three states:

- LEFT DRIFT
- STABLE
- RIGHT DRIFT

A Raspberry Pi processes camera and motion-sensor data and triggers directional vibration feedback to help guide the runner.

## Tech Stack
- Python
- OpenCV
- scikit-learn
- Raspberry Pi 4
- MPU6050 IMU
- GPIO
- Random Forest

## Current Development

The project is currently in progress.

Current work includes:

- Building a synchronized multimodal data collection pipeline
- Collecting and labeling 10,000+ planned samples
- Engineering spatial, temporal, and IMU-based features
- Training and evaluating a Random Forest classifier
- Integrating real-time inference with haptic feedback

## Target Performance

- Classification accuracy: ≥85%
- Processing speed: 20–30 FPS
- Inference latency: <150 ms

## System Flow

Camera + IMU  
↓  
Data Collection  
↓  
Feature Engineering  
↓  
Machine Learning Model  
↓  
Movement Classification  
↓  
Haptic Feedback

## Status

🚧 In active development

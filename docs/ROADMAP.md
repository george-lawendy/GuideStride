# Roadmap

## Completed software foundation

- [x] Repository architecture
- [x] Synthetic 720-frame demo generator
- [x] OpenCV lane/path-boundary baseline
- [x] Lane-center estimation
- [x] Center-error logging
- [x] Temporal drift baseline
- [x] Simulated haptic guidance
- [x] Structured CSV run log
- [x] Raspberry Pi raw data collector scaffold
- [x] Random Forest training/evaluation scaffold
- [x] Unit tests and CI

## In progress

- [ ] Complete repeated Raspberry Pi collection sessions
- [ ] Validate camera/IMU timestamp alignment
- [ ] Define labeling protocol and quality checks
- [ ] Build 10,000+ labeled samples
- [ ] Measure class balance and edge cases

## Next ML milestone

- [ ] Train vision-only Random Forest baseline
- [ ] Train vision + IMU Random Forest baseline
- [ ] Hyperparameter tuning with cross-validation
- [ ] Report accuracy, macro-F1, per-class precision/recall
- [ ] Analyze confusion matrix and failure modes
- [ ] Feature-importance / ablation study

## Edge + hardware milestone

- [ ] Benchmark Raspberry Pi FPS
- [ ] Measure end-to-end response latency
- [ ] Integrate GPIO motor drivers
- [ ] Add confidence-aware motor suppression
- [ ] Log haptic decisions alongside predictions

## Validation milestone

- [ ] Controlled indoor track tests
- [ ] Outdoor lighting/occlusion tests
- [ ] Safety review and human-centered testing protocol
- [ ] Replace engineering targets with measured results

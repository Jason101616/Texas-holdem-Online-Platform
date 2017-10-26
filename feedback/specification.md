Project Specification Feedback
==================

Commit graded: b94632557dff124b7a1c08047a7fc1f60e1051e4

### The product backlog (10/10)

10:  Product backlog is generally complete and adequate. But a spreadsheet-like format may be better. Also, the split work seems to be uneven. Yupeng need to implement the whole Game part, which is the core part in your project. Please reconsider it and adjust.

### Data models (9/10)

9:  Models are generally complete but there are a few problems. First, the participants field in Game play and Desk setup is varchar. But participants and game should be many-to-one relationship. Second, the chip information may change throughout the game, and the desk may has it's own 'chip pool'. 

### Wireframes or mock-ups (10/10)

10: Wireframes are generally complete and adequate.

### Additional Information

This project requires a lot of websockets technologies. Please don't implement your optional features and make friends feature until you have a fully-working game.

---
#### Total score (29/30)
---
Graded by: Sheng Qian (sqian@andrew.cmu.edu)

To view this file with formatting, visit the following page: https://github.com/CMU-Web-Application-Development/<TEAM_NUMBER>/blob/master/feedback/specification-feedback.md

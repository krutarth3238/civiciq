# 🗳️ CivicIQ — AI-Powered Election Process Education Assistant

> Empowering citizens with knowledge. Strengthening democracy through education.

---

## 🎯 Problem Statement Alignment

**Challenge:** PromptWars — Election Process Education  
**Vertical:** Civic Education & Democratic Participation  

CivicIQ tackles one of the most important gaps in modern democracies: a lack of accessible, engaging civic education.

By combining AI with real-world integrations, CivicIQ helps citizens:

- understand elections  
- test their knowledge  
- stay informed and engaged  

---

## 💡 Why CivicIQ Matters

Informed voters are the backbone of democracy — yet civic knowledge is often fragmented, inaccessible, or ignored.

CivicIQ changes that by delivering:

- 🧠 Interactive learning  
- 🎯 Adaptive quizzes  
- 📊 Real progress tracking  
- 📅 Actionable civic reminders  

---

## ⚙️ What CivicIQ Does

CivicIQ is a CLI-based AI civic education platform that:

### 📚 1. Teaches Election Processes

Ask questions like:
- How does voting work?
- What is gerrymandering?

### 🧠 2. Generates Adaptive Quizzes

- Multiple-choice questions  
- Difficulty levels from beginner to advanced  
- Instant feedback and explanations  

### 📊 3. Tracks Learning Progress

- Logs quiz results to Google Sheets  
- Builds a personal civic learning history  

### 📅 4. Manages Civic Awareness

- Adds election reminders to Google Calendar  
- Keeps users informed of key democratic events  

### 📧 5. Sends Learning Summaries

- Uses Gmail API to deliver insights  
- Reinforces long-term retention  

---

## 🏗️ Architecture

```mermaid
sequenceDiagram
participant Citizen
participant CivicIQ CLI
participant GeminiAgent
participant SheetsAPI
participant CalendarAPI
participant GmailAPI

Citizen->>CivicIQ CLI: Ask question / start quiz
CivicIQ CLI->>GeminiAgent: Send prompt
GeminiAgent->>SheetsAPI: Log progress
SheetsAPI-->>GeminiAgent: Confirmation
GeminiAgent->>CalendarAPI: Add reminder
CalendarAPI-->>GeminiAgent: Event created
GeminiAgent->>GmailAPI: Send summary
GmailAPI-->>GeminiAgent: Email sent
GeminiAgent-->>CivicIQ CLI: Response
CivicIQ CLI-->>Citizen: Output

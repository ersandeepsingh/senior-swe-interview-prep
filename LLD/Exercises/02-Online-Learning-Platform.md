# Exercise 2: Online Learning Platform

Design an online learning platform where users can enroll in courses and consume content.

---

## Requirements

1. Student can enroll in a course.
2. Course contains lessons.
3. Lessons can be Video, Article, or Quiz.
4. Video lesson can be played.
5. Article lesson can be read.
6. Quiz lesson can be attempted and scored.
7. Course progress should be tracked.
8. Certificate should be generated after course completion.
9. Notification can be sent via Email or SMS.
10. Payment can be done via UPI or Card.
11. Tomorrow we may add:
  - Live class lesson
    - Wallet payment
    - WhatsApp notification
    - Different certificate formats (PDF or Image)

---



## Design Notes (key corrections)



### 1. Capability methods belong on the object

Prefer `video.Play()` over `Playable.Play(Video)`.

```go
// Bad — method takes the same type it already is
type Playable interface {
	Play(Video)
}

// Good — behavior lives on the lesson
type Playable interface {
	Play() error
}
```

Same idea for `Read()` and `Attempt(...)`.

### 2. Do not force every lesson to implement every capability (ISP)

```go
// Bad — fat lesson interface
type Lesson interface {
	Play() error
	Read() error
	Attempt(answers []string) Score
}

// Good — shared metadata + optional capabilities
type Lesson interface {
	GetID() string
	GetTitle() string
}

type Playable interface {
	Play() error
}

type Readable interface {
	Read() error
}

type Attemptable interface {
	Attempt(answers []string) Score
}
```

Then:

- `VideoLesson` → `Lesson` + `Playable`
- `ArticleLesson` → `Lesson` + `Readable`
- `QuizLesson` → `Lesson` + `Attemptable`



### 3. Progress belongs to enrollment, not the course

Progress is **student + course**, not a field on `Course`:

- Sandeep completed 60% of Go Course
- Amit completed 20% of Go Course

Model it as `Enrollment` / `ProgressTracker`.

### 4. Interface and implementation signatures must match

```go
type NotificationSender interface {
	Send(user User, message string) error
}

// Must match — not Send(amount int)
func (e EmailNotification) Send(user User, message string) error { ... }
```

---



## Domain Models

```go
package main

import "fmt"

type User struct {
	ID      string
	Name    string
	Email   string
	Phone   string
	Address string
}

type Course struct {
	ID      string
	Name    string
	Lessons []Lesson
	Price   float64
}

type Score struct {
	Marks int
}

type Enrollment struct {
	UserID     string
	CourseID   string
	Progress   float64
	IsComplete bool
}
```

---



## Lesson Interfaces

```go
type Lesson interface {
	GetID() string
	GetTitle() string
}

type Playable interface {
	Play() error
}

type Readable interface {
	Read() error
}

type Attemptable interface {
	Attempt(answers []string) Score
}
```

---



## Lesson Types



### Video lesson

```go
type VideoLesson struct {
	ID       string
	Title    string
	VideoURL string
}

func (v VideoLesson) GetID() string    { return v.ID }
func (v VideoLesson) GetTitle() string { return v.Title }

func (v VideoLesson) Play() error {
	fmt.Println("Playing video:", v.VideoURL)
	return nil
}
```



### Article lesson

```go
type ArticleLesson struct {
	ID      string
	Title   string
	Content string
}

func (a ArticleLesson) GetID() string    { return a.ID }
func (a ArticleLesson) GetTitle() string { return a.Title }

func (a ArticleLesson) Read() error {
	fmt.Println("Reading article:", a.Title)
	return nil
}
```



### Quiz lesson

```go
type QuizLesson struct {
	ID        string
	Title     string
	Questions []string
}

func (q QuizLesson) GetID() string    { return q.ID }
func (q QuizLesson) GetTitle() string { return q.Title }

func (q QuizLesson) Attempt(answers []string) Score {
	fmt.Println("Attempting quiz:", q.Title)
	return Score{Marks: 80}
}
```



### Extensibility

Tomorrow: `LiveClassLesson` can implement `Lesson` (+ maybe `Playable` or a new `Joinable`) without changing existing lesson types.

---



## Payment

```go
type PaymentMethod interface {
	Pay(amount float64) error
}

type UPIPayment struct{}

func (u UPIPayment) Pay(amount float64) error {
	fmt.Printf("Paid %.2f using UPI\n", amount)
	return nil
}

type CardPayment struct{}

func (c CardPayment) Pay(amount float64) error {
	fmt.Printf("Paid %.2f using Card\n", amount)
	return nil
}

// Tomorrow: Wallet — no LearningService change
type WalletPayment struct{}

func (w WalletPayment) Pay(amount float64) error {
	fmt.Printf("Paid %.2f using Wallet\n", amount)
	return nil
}
```

---



## Notifications

```go
type NotificationSender interface {
	Send(user User, message string) error
}

type EmailNotification struct{}

func (e EmailNotification) Send(user User, message string) error {
	fmt.Printf("Email sent to %s: %s\n", user.Email, message)
	return nil
}

type SMSNotification struct{}

func (s SMSNotification) Send(user User, message string) error {
	fmt.Printf("SMS sent to %s: %s\n", user.Phone, message)
	return nil
}

// Tomorrow: WhatsApp — no LearningService change
type WhatsAppNotification struct{}

func (w WhatsAppNotification) Send(user User, message string) error {
	fmt.Printf("WhatsApp sent to %s: %s\n", user.Phone, message)
	return nil
}
```

---



## Certificate

```go
type CertificateGenerator interface {
	Generate(course Course, user User) error
}

type PDFCertificateGenerator struct{}

func (p PDFCertificateGenerator) Generate(course Course, user User) error {
	fmt.Printf("PDF certificate generated for %s for course %s\n", user.Name, course.Name)
	return nil
}

type ImageCertificateGenerator struct{}

func (i ImageCertificateGenerator) Generate(course Course, user User) error {
	fmt.Printf("Image certificate generated for %s for course %s\n", user.Name, course.Name)
	return nil
}
```

---



## Progress tracking

```go
type ProgressTracker interface {
	UpdateProgress(user User, course Course, lesson Lesson) (float64, error)
}

type BasicProgressTracker struct{}

func (b BasicProgressTracker) UpdateProgress(user User, course Course, lesson Lesson) (float64, error) {
	fmt.Printf(
		"Updated progress for user %s in course %s after lesson %s\n",
		user.Name,
		course.Name,
		lesson.GetTitle(),
	)
	return 100.0, nil
}
```

---



## LearningService (orchestrator)

Depends on abstractions (DIP). Concrete types are injected from outside.

```go
type LearningService struct {
	PaymentMethod        PaymentMethod
	NotificationSender   NotificationSender
	CertificateGenerator CertificateGenerator
	ProgressTracker      ProgressTracker
}

func (l LearningService) Enroll(user User, course Course) error {
	if err := l.PaymentMethod.Pay(course.Price); err != nil {
		return err
	}

	message := "You have successfully enrolled in " + course.Name
	if err := l.NotificationSender.Send(user, message); err != nil {
		return err
	}

	fmt.Println("Enrollment completed")
	return nil
}

func (l LearningService) CompleteLesson(user User, course Course, lesson Lesson) error {
	progress, err := l.ProgressTracker.UpdateProgress(user, course, lesson)
	if err != nil {
		return err
	}

	if progress >= 100 {
		if err := l.CertificateGenerator.Generate(course, user); err != nil {
			return err
		}
		_ = l.NotificationSender.Send(user, "Congratulations! Your certificate is ready.")
	}

	return nil
}
```

---



## Usage

```go
func main() {
	user := User{
		ID:    "U1",
		Name:  "Sandeep",
		Email: "sandeep@example.com",
		Phone: "9999999999",
	}

	video := VideoLesson{
		ID:       "L1",
		Title:    "Intro to Go",
		VideoURL: "https://video.example.com/go-intro",
	}

	article := ArticleLesson{
		ID:      "L2",
		Title:   "Go Interfaces",
		Content: "Interfaces in Go are implicit...",
	}

	quiz := QuizLesson{
		ID:        "L3",
		Title:     "Go Quiz",
		Questions: []string{"What is an interface?"},
	}

	course := Course{
		ID:      "C1",
		Name:    "Golang LLD",
		Lessons: []Lesson{video, article, quiz},
		Price:   999,
	}

	service := LearningService{
		PaymentMethod:        UPIPayment{},
		NotificationSender:   EmailNotification{},
		CertificateGenerator: PDFCertificateGenerator{},
		ProgressTracker:      BasicProgressTracker{},
	}

	_ = service.Enroll(user, course)

	_ = video.Play()
	_ = article.Read()
	_ = quiz.Attempt([]string{"Answer 1"})

	_ = service.CompleteLesson(user, course, quiz)
}
```

---



## SOLID Evaluation



### 1. SRP — Single Responsibility


| Type                   | Responsibility         |
| ---------------------- | ---------------------- |
| `VideoLesson`          | Video playback         |
| `ArticleLesson`        | Article reading        |
| `QuizLesson`           | Quiz attempt / scoring |
| `PaymentMethod`        | Payment                |
| `NotificationSender`   | Notifications          |
| `CertificateGenerator` | Certificates           |
| `ProgressTracker`      | Progress               |
| `LearningService`      | Orchestration only     |




### 2. OCP — Open/Closed

Add without changing `LearningService`:

- `WalletPayment`
- `WhatsAppNotification`
- `LiveClassLesson`
- `ImageCertificateGenerator`

Only add new structs that implement existing interfaces.

### 3. LSP — Liskov Substitution

Safe substitutions:

- `UPIPayment` / `CardPayment` → `PaymentMethod`
- `EmailNotification` / `SMSNotification` → `NotificationSender`
- `PDFCertificateGenerator` / `ImageCertificateGenerator` → `CertificateGenerator`

Avoided LSP trap: a fat `Lesson` with `Play` + `Read` + `Attempt` would force unsupported behavior.

### 4. ISP — Interface Segregation

This exercise’s main signal.

```go
type Playable interface {
	Play() error
}

type Readable interface {
	Read() error
}

type Attemptable interface {
	Attempt(answers []string) Score
}
```

Video, Article, and Quiz are not forced to implement methods they do not need.

### 5. DIP — Dependency Inversion

`LearningService` depends on:

- `PaymentMethod`
- `NotificationSender`
- `CertificateGenerator`
- `ProgressTracker`

not on `UPIPayment`, `EmailNotification`, etc. Wiring happens outside:

```go
service := LearningService{
	PaymentMethod:        UPIPayment{},
	NotificationSender:   EmailNotification{},
	CertificateGenerator: PDFCertificateGenerator{},
	ProgressTracker:      BasicProgressTracker{},
}
```

---



## Interview-ready summary

Keep `LearningService` as an orchestrator. Depend on abstractions for payment, notification, certificate, and progress. Split lesson capabilities (`Playable` / `Readable` / `Attemptable`) so new lesson types can be added without a fat interface. Put progress on enrollment (student + course), not on the course catalog itself.
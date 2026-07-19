# Exercise 1: Food Delivery Order System

Design a food delivery order flow using SOLID principles in Go.

---

## Requirements

1. User can place a food order.
2. Order contains multiple food items.
3. System validates restaurant availability.
4. System validates item availability.
5. System calculates total price.
6. System applies a coupon.
7. User can pay using UPI, Card, or Wallet.
8. System assigns a delivery partner.
9. System sends notification via Email, SMS, or WhatsApp.
10. Tomorrow we may add:
  - NetBanking payment
    - Slack notification
    - Distance-based delivery assignment
    - Festival coupon

---



## Domain Models

```go
package main

import "fmt"

type Item struct {
	Name      string
	Price     float64
	Available bool
}

type User struct {
	Name    string
	Address string
	Email   string
	Phone   string
}

type Restaurant struct {
	Name   string
	Items  []Item
	IsOpen bool
}

type DeliveryPartner struct {
	Name     string
	Location string
}

type Order struct {
	ID              string
	User            User
	Restaurant      Restaurant
	Items           []Item
	TotalAmount     float64
	DeliveryPartner DeliveryPartner
	IsDelivered     bool
}
```

---



## Interfaces

Small, focused interfaces (ISP). Strategy seams for payment, coupons, delivery, and notifications (OCP).

```go
type RestaurantValidator interface {
	Validate(restaurant Restaurant) error
}

type ItemValidator interface {
	Validate(items []Item) error
}

type PriceCalculator interface {
	Calculate(items []Item) float64
}

type CouponStrategy interface {
	Apply(total float64) float64
}

type PaymentMethod interface {
	Pay(amount float64) error
}

type DeliveryAssignmentStrategy interface {
	Assign(order Order) (DeliveryPartner, error)
}

type NotificationSender interface {
	Send(user User, message string) error
}

type OrderRepository interface {
	Save(order Order) error
}
```



### Avoid a fat interface

```go
// Bad — forces every client to implement everything (ISP violation)
type OrderHandler interface {
	ValidateRestaurant()
	ValidateItems()
	CalculatePrice()
	ApplyCoupon()
	Pay()
	AssignDeliveryPartner()
	SendNotification()
	Save()
}
```

Prefer the small interfaces above.

---



## Implementations



### Validators

```go
type BasicRestaurantValidator struct{}

func (v BasicRestaurantValidator) Validate(restaurant Restaurant) error {
	if !restaurant.IsOpen {
		return fmt.Errorf("restaurant is closed")
	}
	fmt.Println("Restaurant is open")
	return nil
}

type BasicItemValidator struct{}

func (v BasicItemValidator) Validate(items []Item) error {
	for _, item := range items {
		if !item.Available {
			return fmt.Errorf("item %s is not available", item.Name)
		}
	}
	fmt.Println("All items are available")
	return nil
}
```



### Price calculator

```go
type BasicPriceCalculator struct{}

func (p BasicPriceCalculator) Calculate(items []Item) float64 {
	total := 0.0
	for _, item := range items {
		total += item.Price
	}
	return total
}
```



### Coupons

```go
type NoCoupon struct{}

func (n NoCoupon) Apply(total float64) float64 {
	return total
}

type FlatDiscount struct {
	Amount float64
}

func (f FlatDiscount) Apply(total float64) float64 {
	finalTotal := total - f.Amount
	if finalTotal < 0 {
		return 0
	}
	return finalTotal
}

type PercentageDiscount struct {
	Percentage float64
}

func (p PercentageDiscount) Apply(total float64) float64 {
	return total - (total * p.Percentage / 100)
}

// Tomorrow: FestivalCoupon — new struct, same interface
```



### Payment methods

```go
type UPI struct{}

func (u UPI) Pay(amount float64) error {
	fmt.Printf("Payment of %.2f done using UPI\n", amount)
	return nil
}

type Card struct{}

func (c Card) Pay(amount float64) error {
	fmt.Printf("Payment of %.2f done using Card\n", amount)
	return nil
}

type Wallet struct{}

func (w Wallet) Pay(amount float64) error {
	fmt.Printf("Payment of %.2f done using Wallet\n", amount)
	return nil
}

// Tomorrow: NetBanking — add without changing OrderService
type NetBanking struct{}

func (n NetBanking) Pay(amount float64) error {
	fmt.Printf("Payment of %.2f done using NetBanking\n", amount)
	return nil
}
```



### Delivery assignment

```go
type NearestPartnerAssignment struct{}

func (n NearestPartnerAssignment) Assign(order Order) (DeliveryPartner, error) {
	partner := DeliveryPartner{
		Name:     "Rahul",
		Location: "Nearby",
	}
	fmt.Println("Assigned nearest delivery partner:", partner.Name)
	return partner, nil
}

// Tomorrow: DistanceBasedAssignment — same interface, new strategy
type DistanceBasedAssignment struct{}

func (d DistanceBasedAssignment) Assign(order Order) (DeliveryPartner, error) {
	partner := DeliveryPartner{
		Name:     "Amit",
		Location: "3 km away",
	}
	fmt.Println("Assigned delivery partner based on distance:", partner.Name)
	return partner, nil
}
```



### Notifications

```go
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

type WhatsAppNotification struct{}

func (w WhatsAppNotification) Send(user User, message string) error {
	fmt.Printf("WhatsApp sent to %s: %s\n", user.Phone, message)
	return nil
}

// Tomorrow: SlackNotification — no OrderService change
type SlackNotification struct{}

func (s SlackNotification) Send(user User, message string) error {
	fmt.Println("Slack notification sent:", message)
	return nil
}
```



### Repository

```go
type InMemoryOrderRepository struct{}

func (r InMemoryOrderRepository) Save(order Order) error {
	fmt.Println("Order saved:", order.ID)
	return nil
}
```

---



## OrderService (orchestrator)

Depends on **abstractions**, not concrete types (DIP). Concrete dependencies are injected from outside.

```go
type OrderService struct {
	RestaurantValidator RestaurantValidator
	ItemValidator       ItemValidator
	PriceCalculator     PriceCalculator
	CouponStrategy      CouponStrategy
	PaymentMethod       PaymentMethod
	DeliveryStrategy    DeliveryAssignmentStrategy
	NotificationSender  NotificationSender
	OrderRepository     OrderRepository
}

func (o OrderService) PlaceOrder(order Order) error {
	if err := o.RestaurantValidator.Validate(order.Restaurant); err != nil {
		return err
	}

	if err := o.ItemValidator.Validate(order.Items); err != nil {
		return err
	}

	total := o.PriceCalculator.Calculate(order.Items)
	order.TotalAmount = o.CouponStrategy.Apply(total)

	if err := o.PaymentMethod.Pay(order.TotalAmount); err != nil {
		return err
	}

	partner, err := o.DeliveryStrategy.Assign(order)
	if err != nil {
		return err
	}
	order.DeliveryPartner = partner

	if err := o.OrderRepository.Save(order); err != nil {
		return err
	}

	message := fmt.Sprintf("Your order %s has been placed successfully", order.ID)
	return o.NotificationSender.Send(order.User, message)
}
```

---



## Usage

```go
func main() {
	user := User{
		Name:    "Sandeep",
		Address: "Bangalore",
		Email:   "sandeep@example.com",
		Phone:   "9999999999",
	}

	items := []Item{
		{Name: "Pizza", Price: 500, Available: true},
		{Name: "Cold Coffee", Price: 150, Available: true},
	}

	restaurant := Restaurant{
		Name:   "Pizza Palace",
		Items:  items,
		IsOpen: true,
	}

	order := Order{
		ID:         "ORD123",
		User:       user,
		Restaurant: restaurant,
		Items:      items,
	}

	orderService := OrderService{
		RestaurantValidator: BasicRestaurantValidator{},
		ItemValidator:       BasicItemValidator{},
		PriceCalculator:     BasicPriceCalculator{},
		CouponStrategy:      PercentageDiscount{Percentage: 10},
		PaymentMethod:       UPI{},
		DeliveryStrategy:    NearestPartnerAssignment{},
		NotificationSender:  EmailNotification{},
		OrderRepository:     InMemoryOrderRepository{},
	}

	if err := orderService.PlaceOrder(order); err != nil {
		fmt.Println("Order failed:", err)
	}
}
```

---



## SOLID Priciples Apllied



### 1. SRP — Single Responsibility


| Type                  | Responsibility             |
| --------------------- | -------------------------- |
| `RestaurantValidator` | Validates restaurant       |
| `ItemValidator`       | Validates items            |
| `PriceCalculator`     | Calculates total           |
| `CouponStrategy`      | Applies coupon             |
| `PaymentMethod`       | Handles payment            |
| `DeliveryStrategy`    | Assigns delivery partner   |
| `NotificationSender`  | Sends notification         |
| `OrderRepository`     | Persists order             |
| `OrderService`        | Orchestrates the flow only |


`OrderService` does not do everything itself — it only coordinates.

### 2. OCP — Open/Closed

Open for extension, closed for modification. Add without changing `OrderService`:

- NetBanking payment
- Slack notification
- Festival coupon
- Distance-based delivery assignment

Only add new structs that implement existing interfaces.

### 3. LSP — Liskov Substitution

Any `PaymentMethod` implementation should safely replace another:

- `UPI`, `Card`, `Wallet`, `NetBanking` all honor `Pay(amount)`.

**Bad LSP example** — if `Pay()` means *immediate* payment:

```go
type CashOnDelivery struct{}

func (c CashOnDelivery) Pay(amount float64) error {
	return fmt.Errorf("cash on delivery does not pay immediately")
}
```

COD does not honor the same contract — either change the interface (e.g. `Authorize`) or don't put COD behind this `PaymentMethod`.

### 4. ISP — Interface Segregation

Small focused interfaces (`PaymentMethod`, `CouponStrategy`, …) beat one huge `OrderHandler`. Clients depend only on what they need.

### 5. DIP — Dependency Inversion

`OrderService` depends on interfaces, not concretes like `UPI` or `EmailNotification`. Wiring happens outside:

```go
OrderService{
	PaymentMethod:      UPI{},
	NotificationSender: EmailNotification{},
}
```

That is dependency injection and follows DIP.
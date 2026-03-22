"""Minimalny entrypoint aplikacji dla Milestone 0.5."""


def load_stub_config():
    """Zwraca stubowana konfiguracje pojedynczego przebiegu."""
    return {
        "user": "demo-user",
        "items": [
            {
                "name": "Demo Game",
                "link": "https://store.playstation.com/demo-game",
                "base_price": 299.0,
                "current_price": 199.0,
            }
        ],
    }


def detect_discount(item):
    """Okresla, czy dla pozycji wystapila obnizka."""
    base_price = float(item["base_price"])
    current_price = float(item["current_price"])
    has_discount = current_price < base_price
    return {
        "name": item["name"],
        "link": item["link"],
        "base_price": base_price,
        "current_price": current_price,
        "has_discount": has_discount,
    }


def run_price_check():
    """Wykonuje minimalny przebieg end-to-end na stubach."""
    config = load_stub_config()
    results = []
    for item in config["items"]:
        results.append(detect_discount(item))
    return {
        "user": config["user"],
        "results": results,
    }


def build_summary(run_result):
    """Buduje prosty komunikat tekstowy z wyniku przebiegu."""
    discounted_items = [
        item for item in run_result["results"] if item["has_discount"]
    ]
    if not discounted_items:
        return f"Brak obnizek dla {run_result['user']}."

    item = discounted_items[0]
    return (
        f"Wykryto obnizke dla {run_result['user']}: "
        f"{item['name']} z {item['base_price']:.2f} na {item['current_price']:.2f}."
    )


def main():
    """Uruchamia aplikacje i wypisuje wynik minimalnego przebiegu."""
    run_result = run_price_check()
    print(build_summary(run_result))


if __name__ == "__main__":
    main()

"""
Tests for restock order API endpoints.
"""
from datetime import datetime

import pytest

import mock_data


@pytest.fixture(autouse=True)
def reset_restock_orders():
    """Clear submitted restock orders between tests.

    Restock orders live in a module-level list and are never written to disk, so a
    POST in one test would otherwise leak into the next test's GET.
    """
    mock_data.restock_orders.clear()
    yield
    mock_data.restock_orders.clear()


@pytest.fixture
def sample_restock_request():
    """A two-line restock request using known demand forecast SKUs.

    GSK-203 has a 10-day lead time at 6.25 each; MTR-304 has 35 days at 385.00.
    The differing lead times let tests assert the order-level max.
    """
    return {
        "budget": 20000,
        "items": [
            {"item_sku": "GSK-203", "quantity": 600},
            {"item_sku": "MTR-304", "quantity": 35}
        ]
    }


class TestDemandForecastRestockFields:
    """Demand forecasts must carry the fields the Restocking tab prices against."""

    def test_demand_forecasts_include_cost_and_lead_time(self, client):
        """Test that every forecast exposes unit_cost and lead_time_days."""
        response = client.get("/api/demand")
        assert response.status_code == 200

        data = response.json()
        assert len(data) > 0

        for forecast in data:
            assert "unit_cost" in forecast
            assert "lead_time_days" in forecast
            assert isinstance(forecast["unit_cost"], (int, float))
            assert isinstance(forecast["lead_time_days"], int)
            assert forecast["unit_cost"] > 0
            assert forecast["lead_time_days"] > 0


class TestRestockOrderEndpoints:
    """Test suite for restock-order-related endpoints."""

    def test_get_restock_orders_empty(self, client):
        """Test getting restock orders when none have been submitted."""
        response = client.get("/api/restock-orders")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_restock_order(self, client, sample_restock_request):
        """Test submitting a restock order returns the created order."""
        response = client.post("/api/restock-orders", json=sample_restock_request)
        assert response.status_code == 201

        order = response.json()
        assert "id" in order
        assert "restock_number" in order
        assert "items" in order
        assert "total_cost" in order
        assert "budget" in order
        assert "submitted_date" in order
        assert "expected_delivery" in order
        assert "lead_time_days" in order
        assert order["status"] == "Submitted"
        assert order["budget"] == sample_restock_request["budget"]

    def test_restock_number_format(self, client, sample_restock_request):
        """Test that restock numbers use the RST- prefix and are sequential."""
        first = client.post("/api/restock-orders", json=sample_restock_request).json()
        second = client.post("/api/restock-orders", json=sample_restock_request).json()

        assert first["restock_number"].startswith("RST-")
        assert second["restock_number"].startswith("RST-")
        assert first["restock_number"] != second["restock_number"]
        assert first["id"] != second["id"]

    def test_restock_order_items_resolved_from_forecast(self, client, sample_restock_request):
        """Test that item name, unit cost and lead time come from the forecast data."""
        response = client.post("/api/restock-orders", json=sample_restock_request)
        order = response.json()

        assert len(order["items"]) == 2

        gasket = next(i for i in order["items"] if i["item_sku"] == "GSK-203")
        assert gasket["item_name"] == "High-Temperature Gasket"
        assert abs(gasket["unit_cost"] - 6.25) < 0.01
        assert gasket["lead_time_days"] == 10
        assert gasket["quantity"] == 600
        assert abs(gasket["line_cost"] - 600 * 6.25) < 0.01

    def test_restock_order_total_cost_calculation(self, client, sample_restock_request):
        """Test that total cost is the sum of the line costs."""
        response = client.post("/api/restock-orders", json=sample_restock_request)
        order = response.json()

        calculated_total = sum(item["line_cost"] for item in order["items"])
        assert abs(order["total_cost"] - calculated_total) < 0.01
        assert order["total_cost"] <= order["budget"]

    def test_restock_order_lead_time_is_slowest_line(self, client, sample_restock_request):
        """Test that order lead time is the max of the line lead times, not the average."""
        response = client.post("/api/restock-orders", json=sample_restock_request)
        order = response.json()

        line_lead_times = [item["lead_time_days"] for item in order["items"]]
        assert order["lead_time_days"] == max(line_lead_times)
        assert order["lead_time_days"] == 35

    def test_restock_order_expected_delivery_matches_lead_time(self, client, sample_restock_request):
        """Test that expected delivery is the submitted date plus the order lead time."""
        response = client.post("/api/restock-orders", json=sample_restock_request)
        order = response.json()

        submitted = datetime.fromisoformat(order["submitted_date"])
        expected = datetime.fromisoformat(order["expected_delivery"])

        assert (expected - submitted).days == order["lead_time_days"]

    def test_submitted_restock_order_appears_in_list(self, client, sample_restock_request):
        """Test that a submitted order is returned by the list endpoint."""
        created = client.post("/api/restock-orders", json=sample_restock_request).json()

        response = client.get("/api/restock-orders")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["restock_number"] == created["restock_number"]

    def test_restock_orders_returned_newest_first(self, client, sample_restock_request):
        """Test that the most recently submitted order is listed first."""
        client.post("/api/restock-orders", json=sample_restock_request)
        second = client.post("/api/restock-orders", json=sample_restock_request).json()

        data = client.get("/api/restock-orders").json()
        assert len(data) == 2
        assert data[0]["restock_number"] == second["restock_number"]

    def test_restock_order_does_not_affect_sales_orders(self, client, sample_restock_request):
        """Test that submitting a restock leaves sales orders and their totals untouched."""
        before = client.get("/api/dashboard/summary").json()
        order_count_before = len(client.get("/api/orders").json())

        client.post("/api/restock-orders", json=sample_restock_request)

        after = client.get("/api/dashboard/summary").json()
        order_count_after = len(client.get("/api/orders").json())

        assert order_count_after == order_count_before
        assert after["total_orders_value"] == before["total_orders_value"]
        assert after["pending_orders"] == before["pending_orders"]


class TestRestockOrderValidation:
    """Test suite for restock order request validation."""

    def test_reject_empty_items(self, client):
        """Test that a restock order with no items is rejected."""
        response = client.post("/api/restock-orders", json={"budget": 5000, "items": []})
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "item" in data["detail"].lower()

    def test_reject_negative_budget(self, client):
        """Test that a negative budget is rejected."""
        response = client.post("/api/restock-orders", json={
            "budget": -100,
            "items": [{"item_sku": "GSK-203", "quantity": 10}]
        })
        assert response.status_code == 400

        data = response.json()
        assert "budget" in data["detail"].lower()

    def test_reject_unknown_sku(self, client):
        """Test that a SKU with no demand forecast is rejected."""
        response = client.post("/api/restock-orders", json={
            "budget": 5000,
            "items": [{"item_sku": "NOPE-999", "quantity": 10}]
        })
        assert response.status_code == 400

        data = response.json()
        assert "NOPE-999" in data["detail"]

    def test_reject_non_positive_quantity(self, client):
        """Test that a zero or negative quantity is rejected."""
        response = client.post("/api/restock-orders", json={
            "budget": 5000,
            "items": [{"item_sku": "GSK-203", "quantity": 0}]
        })
        assert response.status_code == 400

        data = response.json()
        assert "quantity" in data["detail"].lower()

    def test_reject_missing_budget(self, client):
        """Test that a request without a budget fails schema validation."""
        response = client.post("/api/restock-orders", json={
            "items": [{"item_sku": "GSK-203", "quantity": 10}]
        })
        assert response.status_code == 422

    def test_rejected_request_creates_no_order(self, client):
        """Test that a rejected request leaves the restock order list empty."""
        client.post("/api/restock-orders", json={"budget": 5000, "items": []})

        data = client.get("/api/restock-orders").json()
        assert len(data) == 0

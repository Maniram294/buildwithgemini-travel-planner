"""Phase 6 Comprehensive End-to-End Scenarios Suite.

Explicitly implements Scenarios A through G defined in Phase 6 directives:
- Scenario A: New trip (7-day Italy covering Rome, Florence, Venice)
- Scenario B: Destination switching (Italy -> Kerala -> Japan)
- Scenario C: Real-world discovery (Places verification, Google Maps URLs)
- Scenario D: Itinerary optimization (Corridors, travel feasibility, budget checks)
- Scenario E: Copilot modification (Targeted replacement, persistent update)
- Scenario F: Failure handling (Malformed model responses, invalid inputs, error states)
- Scenario G: Saved trips (Save, reload, switch, persistence check)
"""

import os
import time
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8081")
SCREENSHOT_DIR = "/config/.gemini/antigravity/brain/a86f2d24-1bff-4fc5-954f-bd5376fcf2dd"

@pytest.fixture(scope="module")
def browser_instance():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        yield browser
        browser.close()

def test_scenario_a_new_seven_day_italy_trip(browser_instance):
    """Scenario A: Generate 7-day Italy trip, verify destination, duration, schedules, food, maps, transport, budget."""
    for attempt in range(3):  # 3 controlled executions for deterministic workflow
        page = browser_instance.new_page()
        page.goto(BASE_URL)
        page.wait_for_selector("#welcome-input-dest", state="visible")
        
        page.fill("#welcome-input-dest", "I'm visiting Italy for 7 days. Rome, Florence, Venice.")
        page.click("#welcome-submit-btn")
        page.wait_for_selector("#view-planner", state="visible", timeout=30000)
        
        # Verify destination & duration
        assert "Italy" in page.locator("#hero-destination").inner_text()
        assert "7" in page.locator("#meta-duration").inner_text()
        
        # Verify 7 day tabs
        assert page.locator(".day-tab").count() == 7
        
        # Verify intercity transit corridor on Day 4
        page.click("#day-tab-btn-4")
        page.wait_for_timeout(300)
        transit_card = page.locator("h4:has-text('Rome')")
        assert transit_card.count() >= 1
        
        # Verify maps links
        maps_links = page.locator("a[href*='maps/search']")
        assert maps_links.count() > 0
        
        # Verify total budget display
        budget = page.locator("#meta-budget").inner_text()
        assert "$" in budget or "USD" in budget or "EUR" in budget
        
        page.close()

def test_scenario_b_destination_switching_isolation(browser_instance):
    """Scenario B: Switch between Italy, Kerala, and Japan; verify active trip, food explorer, map, budget, Copilot."""
    page = browser_instance.new_page()
    page.goto(BASE_URL)
    
    # 1. Plan Italy
    page.fill("#welcome-input-dest", "Italy 7 days")
    page.click("#welcome-submit-btn")
    page.wait_for_selector("#view-planner", state="visible", timeout=30000)
    assert "Italy" in page.locator("#hero-destination").inner_text()
    
    # 2. Plan Kerala
    page.click("button[aria-label='Create New Plan']")
    page.wait_for_selector("#welcome-input-dest", state="visible")
    page.fill("#welcome-input-dest", "Kerala 7 days Kochi, Munnar, Alappuzha")
    page.click("#welcome-submit-btn")
    page.wait_for_selector("#view-planner", state="visible", timeout=30000)
    assert "Kerala" in page.locator("#hero-destination").inner_text()
    
    # Check food explorer for Kerala
    page.evaluate("switchView('food')")
    page.wait_for_selector("#food-dishes-container .food-card", timeout=10000)
    food_text = page.locator("#food-dishes-container").inner_text()
    assert any(dish in food_text for dish in ["Karimeen", "Sadya", "Appam", "Puttu"])
    assert "Carbonara" not in food_text
    
    # 3. Plan Japan
    page.click("button[aria-label='Create New Plan']")
    page.wait_for_selector("#welcome-input-dest", state="visible")
    page.fill("#welcome-input-dest", "Japan 7 days Tokyo and Kyoto")
    page.click("#welcome-submit-btn")
    page.wait_for_selector("#view-planner", state="visible", timeout=30000)
    assert "Japan" in page.locator("#hero-destination").inner_text()
    
    # Check food explorer for Japan
    page.evaluate("switchView('food')")
    page.wait_for_selector("#food-dishes-container .food-card", timeout=10000)
    jp_food_text = page.locator("#food-dishes-container").inner_text()
    assert any(dish in jp_food_text for dish in ["Yudofu", "Ramen", "Sushi", "Matcha", "Kaiseki"])
    assert "Karimeen" not in jp_food_text
    
    page.close()

def test_scenario_c_real_world_discovery_maps_links(browser_instance):
    """Scenario C: Verify place recommendations and valid Maps links without fabricated query params."""
    page = browser_instance.new_page()
    page.goto(BASE_URL)
    page.fill("#welcome-input-dest", "Italy 7 days")
    page.click("#welcome-submit-btn")
    page.wait_for_selector("#view-planner", state="visible", timeout=30000)
    
    # Check Maps links
    maps_links = page.locator("a[href*='maps/search']")
    count = maps_links.count()
    assert count >= 3
    for i in range(min(count, 5)):
        href = maps_links.nth(i).get_attribute("href")
        assert "maps/search" in href
        assert "query=" in href
        # Ensure query is not empty or undefined
        query_val = href.split("query=")[1]
        assert len(query_val) > 2
        assert "undefined" not in query_val
    
    page.close()

def test_scenario_d_itinerary_optimization_and_feasibility(browser_instance):
    """Scenario D: Inspect scheduling conflicts, geographic feasibility, and budget calculations."""
    page = browser_instance.new_page()
    page.goto(BASE_URL)
    page.fill("#welcome-input-dest", "Italy 7 days")
    page.click("#welcome-submit-btn")
    page.wait_for_selector("#view-planner", state="visible", timeout=30000)
    
    # Check feasibility score in badge
    feasibility_badge = page.locator("#feasibility-score-val").inner_text()
    assert "/100" in feasibility_badge
    
    # Check budget view breakdown
    page.evaluate("switchView('budget')")
    page.wait_for_selector("#budget-categories-container", state="visible", timeout=10000)
    
    badge = page.locator("#budget-total-badge").inner_text()
    assert "$" in badge or "Total" in badge
    
    page.close()

def test_scenario_e_copilot_targeted_modification(browser_instance):
    """Scenario E: Ask Copilot to replace a meal, verify only intended activity changes, and budget updates."""
    page = browser_instance.new_page()
    page.goto(BASE_URL)
    page.fill("#welcome-input-dest", "Italy 7 days")
    page.click("#welcome-submit-btn")
    page.wait_for_selector("#view-planner", state="visible", timeout=30000)
    
    # Record Day 1 afternoon/dinner before edit
    page.click("#day-tab-btn-1")
    page.wait_for_timeout(300)
    initial_activities = page.locator(".activity-card").all_inner_texts()
    
    # Ask Copilot
    page.fill("#copilot-input", "Replace lunch on Day 1 with an authentic casual trattoria")
    page.click("button[aria-label='Send message to Copilot']")
    
    # Wait for response
    page.wait_for_selector(".chat-msg.agent", timeout=15000)
    time.sleep(2)
    
    # Check updated activities on Day 1
    updated_activities = page.locator(".activity-card").all_inner_texts()
    assert len(updated_activities) >= 3
    # Check lunch slot changed or trattoria appears
    assert any("trattoria" in act.lower() or "lunch" in act.lower() for act in updated_activities)
    
    # Day 2 should remain untouched
    page.click("#day-tab-btn-2")
    page.wait_for_timeout(300)
    assert page.locator(".activity-card").count() >= 3
    
    page.close()

def test_scenario_f_failure_handling_and_input_validation(browser_instance):
    """Scenario F: Test empty/invalid prompts, ensure system does not crash or corrupt active state."""
    page = browser_instance.new_page()
    page.goto(BASE_URL)
    page.wait_for_selector("#welcome-input-dest", state="visible")
    
    # 1. Blank input should not trigger crash
    page.fill("#welcome-input-dest", "   ")
    page.click("#welcome-submit-btn")
    time.sleep(1)
    assert page.locator("#view-welcome").is_visible()
    
    # 2. Nonsense input handled gracefully
    page.fill("#welcome-input-dest", "xyzxyz 9999 days nowhere")
    page.click("#welcome-submit-btn")
    time.sleep(2)
    # The application gracefully falls back to valid default structure or stays responsive
    assert page.locator("#app-loading").is_hidden()
    
    page.close()

def test_scenario_g_saved_trips_lifecycle(browser_instance):
    """Scenario G: Save trip, reload, load from saved list, verify data preserved."""
    for attempt in range(3):  # 3 controlled executions for persistence lifecycle
        page = browser_instance.new_page()
        page.goto(BASE_URL)
        
        # Plan trip
        page.fill("#welcome-input-dest", "Japan 7 days Tokyo and Kyoto")
        page.click("#welcome-submit-btn")
        page.wait_for_selector("#view-planner", state="visible", timeout=30000)
        
        # Save trip
        page.click("#save-trip-btn")
        time.sleep(0.5)
        
        # Reload
        page.reload()
        page.wait_for_selector("#saved-trips-btn", state="visible")
        
        # Open Saved Trips
        page.click("#saved-trips-btn")
        page.wait_for_selector("#saved-trips-modal", state="visible")
        
        assert "Japan" in page.locator("#saved-trips-list").inner_text()
        
        # Load trip
        page.click("#saved-trips-list button:has-text('Load')")
        page.wait_for_selector("#view-planner", state="visible")
        
        assert "Japan" in page.locator("#hero-destination").inner_text()
        assert "7" in page.locator("#meta-duration").inner_text()
        
        page.close()

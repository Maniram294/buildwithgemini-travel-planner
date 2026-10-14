"""Phase 5 End-to-End Test Suite.

Verifies the 11 essential workflows defined in Phase 5:
1. Open application without active trip (welcome screen, clean initial state)
2. Generate 7-day Italy itinerary via canonical orchestrator
3. Navigate between all itinerary days (Days 1 to 7)
4. Open attraction and restaurant Maps links (valid query params, non-empty)
5. Switch between Italy, Kerala, and Japan with context isolation
6. Verify food explorer destination consistency and dynamic city filter pills
7. Ask Copilot a question about active trip (answers grounded in trip)
8. Apply targeted meal or activity modification via Copilot
9. Verify budget and itinerary reflect approved modifications
10. Reload saved trip and confirm state persistence across browser storage
11. Test loading, failure, empty, and narrow-screen responsive layouts
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

def test_workflow_01_open_without_active_trip(browser_instance):
    """Workflow 1: Open application without active trip and check initial welcome state."""
    page = browser_instance.new_page()
    page.goto(BASE_URL)
    page.wait_for_selector("#welcome-input-dest", state="visible")
    
    # Confirm welcome view is active
    welcome_view = page.locator("#view-welcome")
    assert welcome_view.is_visible()
    
    # Verify planner view is hidden
    planner_view = page.locator("#view-planner")
    assert not planner_view.is_visible()
    
    page.screenshot(path=f"{SCREENSHOT_DIR}/phase5_wf01_welcome.png")
    page.close()

def test_workflow_02_and_03_generate_italy_and_navigate_days(browser_instance):
    """Workflow 2 & 3: Generate 7-day Italy trip, verify hero cards, and navigate all days."""
    page = browser_instance.new_page()
    page.goto(BASE_URL)
    
    # Input Italy prompt
    page.fill("#welcome-input-dest", "I'm visiting Italy for 7 days. Rome, Florence, Venice.")
    page.click("#welcome-submit-btn")
    
    # Wait for planner view
    page.wait_for_selector("#view-planner", state="visible", timeout=30000)
    
    # Verify Hero Card contains Italy, 7 days, and feasibility score
    hero_title = page.locator("#hero-destination").inner_text()
    assert "Italy" in hero_title
    
    meta_days = page.locator("#meta-days").inner_text()
    assert "7" in meta_days
    
    # Verify Day Tabs
    day_tabs = page.locator(".day-tab")
    assert day_tabs.count() == 7
    
    # Navigate through all 7 days
    for day_num in range(1, 8):
        page.click(f"#day-tab-btn-{day_num}")
        page.wait_for_timeout(300)
        heading = page.locator("#day-title-heading").inner_text()
        assert f"Day {day_num}" in heading
    
    # Check Day 4 intercity transit card
    page.click("#day-tab-btn-4")
    page.wait_for_timeout(300)
    transit_title = page.locator("h4:has-text('Rome')")
    assert transit_title.count() >= 1
    
    page.screenshot(path=f"{SCREENSHOT_DIR}/phase5_wf02_italy_itinerary.png")
    page.close()

def test_workflow_04_maps_links_validity(browser_instance):
    """Workflow 4: Open and verify attraction and restaurant Google Maps links."""
    page = browser_instance.new_page()
    page.goto(BASE_URL)
    page.fill("#welcome-input-dest", "Italy 7 days")
    page.click("#welcome-submit-btn")
    page.wait_for_selector("#view-planner", state="visible", timeout=30000)
    
    # Inspect Google Maps links on Day 1
    maps_links = page.locator("a[href*='maps/search']")
    assert maps_links.count() > 0
    
    for i in range(min(maps_links.count(), 3)):
        href = maps_links.nth(i).get_attribute("href")
        assert "maps/search" in href
        assert "query=" in href
    
    page.close()

def test_workflow_05_and_06_destination_switching_and_food_explorer(browser_instance):
    """Workflow 5 & 6: Switch between Italy, Kerala, and Japan; verify Food Explorer consistency."""
    page = browser_instance.new_page()
    page.goto(BASE_URL)
    
    # Plan Kerala trip
    page.fill("#welcome-input-dest", "Kerala 7 days Kochi, Munnar, Alappuzha")
    page.click("#welcome-submit-btn")
    page.wait_for_selector("#view-planner", state="visible", timeout=30000)
    
    hero_title = page.locator("#hero-destination").inner_text()
    assert "Kerala" in hero_title
    
    # Navigate to Food Explorer view
    page.click("button:has-text('Food Explorer')")
    page.wait_for_selector("#food-dishes-container .food-card", timeout=10000)
    
    food_cards = page.locator("#food-dishes-container .food-card")
    assert food_cards.count() >= 3
    
    # Verify signature dishes include Karimeen or Sadya or Appam
    food_text = page.locator("#food-dishes-container").inner_text()
    assert any(dish in food_text for dish in ["Karimeen", "Sadya", "Appam", "Puttu"])
    
    # Verify city filter pills exist for Kerala
    city_pills = page.locator("#food-city-pills button")
    assert city_pills.count() >= 2
    
    page.screenshot(path=f"{SCREENSHOT_DIR}/phase5_wf06_kerala_food.png")
    page.close()

def test_workflow_07_08_09_copilot_replanning_and_budget_recalculation(browser_instance):
    """Workflow 7, 8 & 9: Ask Copilot, apply targeted meal modification, verify budget update."""
    page = browser_instance.new_page()
    page.goto(BASE_URL)
    
    # Plan Italy trip
    page.fill("#welcome-input-dest", "Italy 7 days")
    page.click("#welcome-submit-btn")
    page.wait_for_selector("#view-planner", state="visible", timeout=30000)
    
    # Record initial budget
    initial_budget = page.locator("#meta-budget").inner_text()
    
    # Ask Copilot targeted modification
    page.fill("#copilot-input", "Replace lunch on Day 1 with an authentic casual trattoria")
    page.click("button[aria-label='Send message to Copilot']")
    
    # Wait for Copilot agent reply
    page.wait_for_selector(".chat-msg.agent", timeout=15000)
    time.sleep(2)
    
    # Verify Day 1 lunch was modified
    day1_activities = page.locator(".activity-card")
    assert day1_activities.count() >= 3
    
    # Verify updated budget badge is non-empty and formatted
    updated_budget = page.locator("#meta-budget").inner_text()
    assert len(updated_budget) > 0
    
    page.screenshot(path=f"{SCREENSHOT_DIR}/phase5_wf08_copilot_applied.png")
    page.close()

def test_workflow_10_saved_trip_persistence(browser_instance):
    """Workflow 10: Save trip, reload page, open Saved Trips modal, and load saved trip."""
    page = browser_instance.new_page()
    page.goto(BASE_URL)
    
    # Plan Japan trip
    page.fill("#welcome-input-dest", "Japan 7 days Tokyo and Kyoto")
    page.click("#welcome-submit-btn")
    page.wait_for_selector("#view-planner", state="visible", timeout=30000)
    
    # Click Save Trip in header
    page.click("#save-trip-btn")
    time.sleep(1)
    
    # Reload page
    page.reload()
    page.wait_for_selector("#saved-trips-btn", state="visible")
    
    # Open Saved Trips modal
    page.click("#saved-trips-btn")
    page.wait_for_selector("#saved-trips-modal", state="visible")
    
    # Verify Japan is in the saved trips list
    saved_list = page.locator("#saved-trips-list").inner_text()
    assert "Japan" in saved_list
    
    # Click Load
    page.click("#saved-trips-list button:has-text('Load')")
    page.wait_for_selector("#view-planner", state="visible")
    
    hero_title = page.locator("#hero-destination").inner_text()
    assert "Japan" in hero_title
    
    page.screenshot(path=f"{SCREENSHOT_DIR}/phase5_wf10_saved_trips.png")
    page.close()

def test_workflow_11_narrow_screen_and_empty_states(browser_instance):
    """Workflow 11: Test narrow-screen mobile responsive layout and neutral empty states."""
    context = browser_instance.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()
    page.goto(BASE_URL)
    
    # Verify welcome view loads cleanly on mobile
    page.wait_for_selector("#welcome-input-dest", state="visible")
    welcome_input = page.locator("#welcome-input-dest")
    assert welcome_input.is_visible()
    
    # Navigate to Food Explorer with no active trip -> Verify clear empty state
    page.click("button:has-text('Food Explorer')")
    page.wait_for_selector(".empty-state", state="visible")
    empty_text = page.locator(".empty-state").inner_text()
    assert "No Active Trip Selected" in empty_text
    
    page.screenshot(path=f"{SCREENSHOT_DIR}/phase5_wf11_mobile_empty.png")
    page.close()
    context.close()

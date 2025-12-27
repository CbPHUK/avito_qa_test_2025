package tests

import (
    "bytes"
    "encoding/json"
    "net/http"
    "strconv"
    "testing"
)

const (
    BASE_URL = "https://qa-internship.avito.com"
    sellerID = 999999
)

func createTestAd(t *testing.T) string {
    t.Helper()

    payload := map[string]interface{}{
        "name":     "Test Ad from internship",
        "price":    1000,
        "sellerId": sellerID,
        "statistics": map[string]int{
            "contacts":  0,
            "likes":     0,
            "viewCount": 0,
        },
    }

    jsonData, err := json.Marshal(payload)
    if err != nil {
        t.Fatal(err)
    }

    resp, err := http.Post(BASE_URL+"/api/1/item", "application/json", bytes.NewBuffer(jsonData))
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        t.Fatalf("Expected status 200, got %d", resp.StatusCode)
    }

    var result map[string]interface{}
    if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
        t.Fatal(err)
    }

    adID, ok := result["id"].(string)
    if !ok {
        t.Fatal("ID not found or not string in response")
    }

    t.Cleanup(func() {
        req, _ := http.NewRequest("DELETE", BASE_URL+"/api/2/item/"+adID, nil)
        http.DefaultClient.Do(req)
    })

    return adID
}

func TestCreateAdvertisement(t *testing.T) {
    payload := map[string]interface{}{
        "name":     "Simple Test Ad",
        "price":    500,
        "sellerId": sellerID,
        "statistics": map[string]int{
            "contacts":  0,
            "likes":     0,
            "viewCount": 0,
        },
    }

    jsonData, _ := json.Marshal(payload)
    resp, err := http.Post(BASE_URL+"/api/1/item", "application/json", bytes.NewBuffer(jsonData))
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        t.Errorf("Expected status 200, got %d", resp.StatusCode)
    }

    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)

    if _, exists := result["id"]; !exists {
        t.Error("Expected 'id' in response")
    }
}

func TestGetAdvertisementByID(t *testing.T) {
    adID := createTestAd(t)

    resp, err := http.Get(BASE_URL + "/api/1/item/" + adID)
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        t.Errorf("Expected status 200, got %d", resp.StatusCode)
    }

    var data []map[string]interface{}
    if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
        t.Fatal(err)
    }

    if len(data) == 0 {
        t.Fatal("No data returned")
    }

    if data[0]["id"].(string) != adID {
        t.Error("Returned ad ID does not match created")
    }
}

func TestGetAdvertisementsBySeller(t *testing.T) {
    adID := createTestAd(t)

    resp, err := http.Get(BASE_URL + "/api/1/" + strconv.Itoa(sellerID) + "/item")
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        t.Errorf("Expected status 200, got %d", resp.StatusCode)
    }

    var ads []map[string]interface{}
    if err := json.NewDecoder(resp.Body).Decode(&ads); err != nil {
        t.Fatal(err)
    }

    found := false
    for _, ad := range ads {
        if ad["id"].(string) == adID {
            found = true
            break
        }
    }

    if !found {
        t.Error("Created ad not found in seller's list")
    }
}

func TestGetStatistics(t *testing.T) {
    adID := createTestAd(t)

    resp, err := http.Get(BASE_URL + "/api/1/statistic/" + adID)
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        t.Errorf("Expected status 200, got %d", resp.StatusCode)
    }

    var stats []map[string]interface{}
    if err := json.NewDecoder(resp.Body).Decode(&stats); err != nil {
        t.Fatal(err)
    }

    if len(stats) == 0 {
        t.Error("No statistics returned")
    }

    stat := stats[0]
    fields := []string{"likes", "viewCount", "contacts"}
    for _, field := range fields {
        if _, exists := stat[field]; !exists {
            t.Errorf("Field %s missing in statistics", field)
        }
    }
}

func TestDeleteAdvertisement(t *testing.T) {
    adID := createTestAd(t)

    req, err := http.NewRequest("DELETE", BASE_URL+"/api/2/item/"+adID, nil)
    if err != nil {
        t.Fatal(err)
    }

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        t.Errorf("Expected status 200, got %d", resp.StatusCode)
    }
}

// Негативные тесты

func TestGetNonExistentAdvertisement(t *testing.T) {
    resp, err := http.Get(BASE_URL + "/api/1/item/nonexistent123")
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusNotFound {
        t.Errorf("Expected status 404, got %d", resp.StatusCode)
    }
}

func TestGetNonExistentStatistics(t *testing.T) {
    resp, err := http.Get(BASE_URL + "/api/1/statistic/nonexistent123")
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusNotFound {
        t.Errorf("Expected status 404, got %d", resp.StatusCode)
    }
}

func TestDeleteNonExistentAdvertisement(t *testing.T) {
    req, err := http.NewRequest("DELETE", BASE_URL+"/api/2/item/nonexistent123", nil)
    if err != nil {
        t.Fatal(err)
    }

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusNotFound {
        t.Errorf("Expected status 404, got %d", resp.StatusCode)
    }
}

func TestCreateAdvertisementWithoutName(t *testing.T) {
    payload := map[string]interface{}{
        "price": 500,
        "sellerId": sellerID,
        "statistics": map[string]int{
            "contacts":  0,
            "likes":     0,
            "viewCount": 0,
        },
    }

    jsonData, _ := json.Marshal(payload)
    resp, err := http.Post(BASE_URL+"/api/1/item", "application/json", bytes.NewBuffer(jsonData))
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusBadRequest {
        t.Errorf("Expected status 400 (missing name), got %d", resp.StatusCode)
    }
}

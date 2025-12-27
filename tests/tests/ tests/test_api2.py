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
)

var uniqueSellerID = 999999 


func createTestAd(t *testing.T) string {
    t.Helper()

    payload := map[string]interface{}{
        "name":     "Test Ad from internship",
        "price":    1000,
        "sellerId": uniqueSellerID,
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

func TestCreateAd(t *testing.T) {
    payload := map[string]interface{}{
        "name":     "Test Ad",
        "price":    500,
        "sellerId": uniqueSellerID,
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

func TestGetAd(t *testing.T) {
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

    if len(data) == 0 || data[0]["id"].(string) != adID {
        t.Error("Ad ID does not match")
    }
}

func TestGetAdsBySeller(t *testing.T) {
    adID := createTestAd(t)

    resp, err := http.Get(BASE_URL + "/api/1/" + strconv.Itoa(uniqueSellerID) + "/item")
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
    if _, exists := stat["likes"]; !exists {
        t.Error("likes field missing")
    }
}

func TestDeleteAd(t *testing.T) {
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

func TestGetNonExistentAd(t *testing.T) {
    resp, err := http.Get(BASE_URL + "/api/1/item/nonexistent")
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusNotFound {
        t.Errorf("Expected status 404, got %d", resp.StatusCode)
    }
}

func TestDeleteNonExistent(t *testing.T) {
    req, err := http.NewRequest("DELETE", BASE_URL+"/api/2/item/nonexistent", nil)
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

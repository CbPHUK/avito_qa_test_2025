package main

import (
	'encoding/json'
	'fmt'
	'net/http'
	'strconv'
	'testing'
)

const BASE_URL = 'https://qa-internship.avito.com'

var sellerID = 999999

func createTestAd(t *testing.T) int {
	payload := map[string]interface{}{
		'name':     'Test Ad from Grok',
		'price':    1000,
		'sellerId': sellerID,
		'statistics': map[string]int{
			'contacts':  0,
			'likes':     0,
			'viewCount': 0,
		},
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(BASE_URL+'/api/1/item', 'application/json', bytes.NewBuffer(jsonData))
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		t.Fatalf('Expected status 200, got %d', resp.StatusCode)
	}

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)

	adID := int(result['id'].(float64))
	return adID
}

func TestCreateAd(t *testing.T) {
	payload := map[string]interface{}{
		'name':     'Test Ad',
		'price':    500,
		'sellerId': sellerID,
		'statistics': map[string]int{
			'contacts':  0,
			'likes':     0,
			'viewCount': 0,
		},
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(BASE_URL+'/api/1/item', 'application/json', bytes.NewBuffer(jsonData))
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		t.Errorf('Expected status 200, got %d', resp.StatusCode)
	}

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)

	if _, exists := result['id']; !exists {
		t.Error('Expected id in response')
	}

	if id, ok := result['id'].(float64); ok {
		req, _ := http.NewRequest('DELETE', BASE_URL+'/api/2/item/'+strconv.Itoa(int(id)), nil)
		http.DefaultClient.Do(req)
	}
}

func TestGetAd(t *testing.T) {
	
	adID := createTestAd(t)

	resp, err := http.Get(BASE_URL + '/api/1/item/' + strconv.Itoa(adID))
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		t.Errorf('Expected status 200, got %d', resp.StatusCode)
	}

	var data []map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&data)

	if len(data) == 0 || int(data[0]['id'].(float64)) != adID {
		t.Error('Ad ID does not match')
	}

	
	req, _ := http.NewRequest('DELETE', BASE_URL+'/api/2/item/'+strconv.Itoa(adID), nil)
	http.DefaultClient.Do(req)
}

func TestGetAdsBySeller(t *testing.T) {
	
	adID := createTestAd(t)

	resp, err := http.Get(BASE_URL + '/api/1/' + strconv.Itoa(sellerID) + '/item')
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		t.Errorf('Expected status 200, got %d', resp.StatusCode)
	}

	var ads []map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&ads)

	found := false
	for _, ad := range ads {
		if int(ad['id'].(float64)) == adID {
			found = true
			break
		}
	}

	if !found {
		t.Error('Created ad not found in seller ads list')
	}

	
	req, _ := http.NewRequest('DELETE', BASE_URL+'/api/2/item/'+strconv.Itoa(adID), nil)
	http.DefaultClient.Do(req)
}

func TestGetStatistics(t *testing.T) {
	
	adID := createTestAd(t)

	resp, err := http.Get(BASE_URL + '/api/1/statistic/' + strconv.Itoa(adID))
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		t.Errorf('Expected status 200, got %d', resp.StatusCode)
	}

	var stats []map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&stats)

	if len(stats) == 0 {
		t.Error('No statistics returned')
	}

	stat := stats[0]
	if _, exists := stat['likes']; !exists {
		t.Error('likes field missing')
	}
	if _, exists := stat['viewCount']; !exists {
		t.Error('viewCount field missing')
	}
	if _, exists := stat['contacts']; !exists {
		t.Error('contacts field missing')
	}

	
	req, _ := http.NewRequest('DELETE', BASE_URL+'/api/2/item/'+strconv.Itoa(adID), nil)
	http.DefaultClient.Do(req)
}

func TestDeleteAd(t *testing.T) {
	
	adID := createTestAd(t)

	req, err := http.NewRequest('DELETE', BASE_URL+'/api/2/item/'+strconv.Itoa(adID), nil)
	if err != nil {
		t.Fatal(err)
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		t.Errorf('Expected status 200, got %d', resp.StatusCode)
	}
}

// Негативные тесты
func TestGetNonExistentAd(t *testing.T) {
	resp, err := http.Get(BASE_URL + '/api/1/item/nonexistent123')
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 404 {
		t.Errorf('Expected status 404, got %d', resp.StatusCode)
	}
}

func main() {
	fmt.Println('Запуск тестов...')
	// В Go тесты запускаются через 'go test', но для примера:
	t := &testing.T{}
	TestCreateAd(t)
	TestGetAd(t)
	TestGetAdsBySeller(t)
	TestGetStatistics(t)
	TestDeleteAd(t)
	TestGetNonExistentAd(t)
}

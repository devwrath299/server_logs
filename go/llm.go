
package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"google.golang.org/api/option"
	"google.golang.org/api/sheets/v4"
)

type LogEntry struct {
	IP          string `json:"ip"`
	UserAgent   string `json:"user_agent"`
	Referrer    string `json:"referrer"`
	RequestPath string `json:"request_path"`
	Timestamp   string `json:"timestamp"`
}

// Send logs to Python LLM for analysis
func sendLogsToPythonLLM(logs []LogEntry) (string, error) {
	logData, err := json.Marshal(logs)
	if err != nil {
		return "", err
	}

	// Python API URL
	apiURL := "http://localhost:5000/analyze" // URL of the Python API
	req, err := http.NewRequest("POST", apiURL, bytes.NewBuffer(logData))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	return string(body), nil
}

// API handler for analyzing logs
func analyzeLogsHandler(c *gin.Context) {
	apiKey := "AIzaSyAhIRPXDC7G_rxNRbCVrSkxcLoX36h9dN4" // Replace with your actual API key

	ctx := context.Background()
	service, err := sheets.NewService(ctx, option.WithAPIKey(apiKey))
	if err != nil {
		c.String(http.StatusInternalServerError, "Unable to retrieve Sheets client: %v", err)
		return
	}

	spreadsheetID := "1j_EdilCL5Jm-ekHli3VY2zf98lQOdOwo4lri9N3PvkY" // Replace with your actual spreadsheet ID
	readRange := "Sheet1!A2:F5001"            // Assuming your data starts from A2

	resp, err := service.Spreadsheets.Values.Get(spreadsheetID, readRange).Do()
	if err != nil {
		c.String(http.StatusInternalServerError, "Unable to retrieve data from sheet: %v", err)
		return
	}

	var logs []LogEntry
	for _, row := range resp.Values {
		// Assuming columns are: IP, UserAgent, Referrer, RequestPath, Timestamp
		logEntry := LogEntry{
			IP:          fmt.Sprintf("%v", row[0]), // Convert interface{} to string
			UserAgent:   fmt.Sprintf("%v", row[1]),
			Referrer:    fmt.Sprintf("%v", row[2]),
			RequestPath: fmt.Sprintf("%v", row[3]),
			Timestamp:   fmt.Sprintf("%v", row[4]),
		}
		logs = append(logs, logEntry)
	}

	fmt.Println("logs size",len(logs))

	classifications, err := sendLogsToPythonLLM(logs)
	if err != nil {
		c.String(http.StatusInternalServerError, "Error: %v", err)
		return
	}

	// Return the classifications as plain text response
	c.String(http.StatusOK, classifications)
}

func main() {
	r := gin.Default()
	r.POST("/analyze-logs", analyzeLogsHandler) // Change to GET method for simplicity
	fmt.Println("Starting server on :8080...")
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}




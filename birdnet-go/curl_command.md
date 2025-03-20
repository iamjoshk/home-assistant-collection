This curl command queries my Birdweather station and creates an HA entity with a state of total detections and attributes with total detections, last detection datetime, last query response datetime, most recent species detected, most recent species detected image URL, and the 100 most recent detections, grouped by species name (common name) with a count, scientific name, last species detection, and an image URL for a picture.

2025-03-20: Updated to include ebirdUrl for most recent detection and 100 most recent detections.

```
command_line:
  - sensor:
      name: "Birdweather Detections Station xxxxxx"
      unique_id: birdweather_detections_station_xxxxxx
      availability: "{{ value_json is defined }}"
      command: >
        curl -s \
          -H "Content-Type: application/json" \
          --data '{
              "query": "query StationDetections($stationId: ID!, $first: Int) { station(id: $stationId) { id detections(first: $first) { totalCount nodes { timestamp species { id commonName imageUrl scientificName ebirdUrl } speciesId confidence } } } }",
              "variables": { "stationId": "xxxxxx", "first": 100 }
            }' \
          "https://app.birdweather.com/graphql" | jq --arg now "$(date -Is)" '{
            stationId: .data.station.id,
            totalDetections: .data.station.detections.totalCount,
            lastDetection: (
              .data.station.detections.nodes |
              map(.timestamp) |  # Extract all timestamps
              max  # Find the maximum (latest) timestamp
            ),
            mostRecentSpeciesName: (
              .data.station.detections.nodes[0].species.commonName // "None" # Species name of the most recent bird
            ),
            mostRecentSpeciesImageUrl: (
              .data.station.detections.nodes[0].species.imageUrl // "None" # Image URL of the most recent bird
            ),
            mostRecentSpeciesEbirdUrl: (
              .data.station.detections.nodes[0].species.ebirdUrl // "None" # Image URL of the most recent bird
            ),
            species: (
              .data.station.detections.nodes |
              group_by(.species.commonName) |
              map(
                {
                  speciesName: .[0].species.commonName,
                  totalCount: length,
                  lastSpeciesDetection: (
                    sort_by(.timestamp) |  # Sort by timestamp within the group
                    .[length - 1].timestamp   # Get the last (latest) timestamp
                  ),
                  scientificName: .[0].species.scientificName,
                  imageUrl: .[0].species.imageUrl,
                  ebirdUrl: .[0].species.ebirdUrl
                }
              )
            ),
            lastResponse: $now
          }'
      scan_interval: 59
      unit_of_measurement: ''
      value_template: >
        {{ value_json.totalDetections }}
      json_attributes:
        - totalDetections
        - stationId
        - mostRecentSpeciesName
        - mostRecentSpeciesImageUrl
        - mostRecentSpeciesEbirdUrl
        - lastDetection
        - lastResponse
        - species
```

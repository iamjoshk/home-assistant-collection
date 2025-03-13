I use two different `flex-table-card` cards on my dashboards. One for mobile dashboard and one for a tablet or desktop dashboard.

---


### Tablet/Desktop Dashboard version:
This version creates a horizontal view, by using `card_mod` to create multiple columns in the card. 

![desktop_dashboard_birdweather](https://github.com/user-attachments/assets/3aace39a-5259-4eab-86ca-a8759c75f3ad)



```
type: custom:flex-table-card
title: 100 Most Recent Detections
entities:
  - entity: sensor.birdweather_detections_station_nnnnn
columns:
  - name: ""
    data: species.imageUrl
    modify: "'<img src=\"' + x + '\"style: width=75%; height=auto;\">'"
  - name: ""
    data: species
    modify: >
      "<strong><span style=\"text-transform: uppercase;\">" + x.speciesName +
      "</span></strong>" + 

      "<br>" + 

      "Count: " + x.totalCount +

      "<br>" + 

      "Scientific Name: " + x.scientificName +

      "<br>" + 

      "Last Detection: " + x.lastSpeciesDetection.substring(0, 10)
search: true
grid_options:
  columns: 48
  rows: auto
card_mod:
  style: |
    table {
      /*Remove table styles to prevent style conflicts*/
      display:table !important;
    }
    tbody {
      display: grid !important;
      grid-template-columns: repeat(4, 1fr);
      grid-gap: 10px;
    }

    tr {
      grid-column: auto;
    }

    td {
      float: none !important;
      display: table-cell !important;
      width: auto !important;
      max-width: none !important;
    }

    thead {
      display: none !important; /* Hide the table header if you don't need it */
    }

    tfoot {
      display: none !important; /*Hide the footer if you dont need it*/
    }
```


### Mobile view:
This version retains the typical vertical format of `flex-table-card`.

![mobile_dashboard_birdweather_50](https://github.com/user-attachments/assets/40033315-8bf2-47bd-bbfb-f04b16e3da00)


```
type: custom:flex-table-card
title: 100 Most Recent Detections
entities:
  - entity: sensor.birdweather_detections_station_12159
columns:
  - name: ""
    data: species.imageUrl
    modify: "'<img src=\"' + x + '\"style: width=75%; height=auto;\">'"
  - name: ""
    data: species
    modify: >
      "<strong><span style=\"text-transform: uppercase;\">" + x.speciesName +
      "</span></strong>" + 

      "<br>" + 

      "Count: " + x.totalCount +

      "<br>" + 

      "Scientific Name: " + x.scientificName +

      "<br>" + 

      "Last Detection: " + x.lastSpeciesDetection.substring(0, 10)
search: true
grid_options:
  columns: 24
  rows: auto
```



---
NOTES:
- I use a version of `flex-table-card` that I forked and added a search filter field at the top of the card to let me filter the data (or birds) that I want to see.
  I make no claims of quality: https://github.com/iamjoshk/flex-table-card
    

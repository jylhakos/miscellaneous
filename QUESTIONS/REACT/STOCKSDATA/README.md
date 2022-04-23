# React: STOCKS DATA

## Requirements

- The input should initially be empty. The user can type a date in this input box, for which the stock data has to be searched. The date format has to be d-mmmm-yyyy (e.g., 5-January-2000).

- Clicking on the 'Search' button should make an API GET call to URL `https://jsonmock.hackerrank.com/api/stocks?date={input}` 

For example, for date 5-January-2000, the API hit has to be `https://jsonmock.hackerrank.com/api/stocks?date=5-January-2000`.

- The response will contain a data:
```
{
  "data": [
    {
      "date": "5-January-2000",
      "open": 5265.09,
      "high": 5464.35,
      "low": 5184.48,
      "close": 5357
    }
  ]
}
```

- The data field is an array containing single object.

- Display the data inside `<ul data-testid="stock-data"></ul>`. This list will have the following list elements(in order as mentioned below):
  * `<li>Open: {open}</li>`, where {open} is the open value received from data above
  * `<li>Close: {close}</li>`, where {close} is the close value received from data above
  * `<li>High: {high}</li>`, where {high} is the high value received from data above
  * `<li>Low: {low}</li>`, where {low} is the low value received from data above

- The element `<ul data-testid="stock-data"></ul>` is rendered only when data is fetched and the result is shown. Initially, it is not rendered since no API has been hit yet.

- If there is no stock data returned by the API, the user should render `<div data-testid="no-result">No Results Found</div>` instead of the `<ul>` element.

- Please note that the input field accepts the date as text. Input will be tested only with valid dates, so writing input validation is not required.

## Testing

- Input should have the data-testid attribute 'app-input'.
- Search button should have the data-testid attribute 'submit-button'.
- `<ul>` should have the data-testid attribute 'stock-data'.
- The 'No Results Found' div should have the data-testid attribute 'no-result'.

**Commands**
- run: 
```bash
bash bin/env_setup && . $HOME/.nvm/nvm.sh && npm start
```
- install:
```bash
bash bin/env_setup && . $HOME/.nvm/nvm.sh && npm install
```
- test: 
```bash
bash bin/env_setup && . $HOME/.nvm/nvm.sh && npm test
```

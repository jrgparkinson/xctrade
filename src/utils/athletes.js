

export function formatPercentChange(percent_change) {
  let change = percent_change;
  let changeColor = 'red';
  if (change == null) {
    change = 'N/A';
  } else {
    change = Number(change).toFixed(0);
    if (change >= 0) {
      change = '+' + change;
      changeColor='green';
    }
    change = change + '%';
  }
  return {change: change, changeColor: changeColor};
}

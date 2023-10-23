
/**
 * Limits left min knob of dual range slider to max knob
 */
function controlFromSlider(fromSlider, toSlider, fromLabel, minDate) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, toSlider);
  if (from > to) {
    fromSlider.value = to;
  }
  fromLabel.innerText = serializeDate(getSelectedDateRange(fromSlider, toSlider, minDate)[0]);
  updateProtocolFilter();
}

/**
 * Limits right max knob of dual range slider to min knob
 */
function controlToSlider(fromSlider, toSlider, toLabel, minDate) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, toSlider);
  setToggleAccessible(toSlider);
  if (from > to) {
    toSlider.value = from;
  }
  toLabel.innerText = serializeDate(getSelectedDateRange(fromSlider, toSlider, minDate)[1]);
  updateProtocolFilter();
}

/**
 * @returns a value pair of the current values of the sliders
 */
function getParsed(currentFrom, currentTo) {
  const from = parseInt(currentFrom.value, 10);
  const to = parseInt(currentTo.value, 10);
  return [from, to];
}

const rangeColor = 'var(--accent-color)';
const sliderColor = 'var(--card-color)';

/**
 * Highlights the range between the two knobs of the dual range slider
 */
function fillSlider(from, to, controlSlider) {
    const rangeDistance = to.max-to.min;
    const fromPosition = from.value - to.min;
    const toPosition = to.value - to.min;
    controlSlider.style.background = `linear-gradient(
      to right,
      ${sliderColor} 0%,
      ${sliderColor} ${(fromPosition)/(rangeDistance)*100}%,
      ${rangeColor} ${((fromPosition)/(rangeDistance))*100}%,
      ${rangeColor} ${(toPosition)/(rangeDistance)*100}%, 
      ${sliderColor} ${(toPosition)/(rangeDistance)*100}%, 
      ${sliderColor} 100%)`;
}

/**
 * Brings right knob to front
 */
function setToggleAccessible(currentTarget) {
  const toSlider = document.querySelector('#toSlider');
  if (Number(currentTarget.value) <= 0 ) {
    toSlider.style.zIndex = 2;
  } else {
    toSlider.style.zIndex = 0;
  }
}

/**
 * @returns a map of protocol numbers to their dates
 */
function findProtocolDates() {
  const protocols = document.querySelectorAll('.container');
  const procolDates = {};
  const datePattern = /^\d{2}\.\d{2}\.\d{4}$/

  protocols.forEach((container) => {
    const dateString = container.querySelector('.date').textContent;

    if (!datePattern.test(dateString)) {
      return;
    }
    const [day, month, year] = dateString.split('.');
    const date = new Date(year, month - 1, day)

    const containerId = container.id;
    const protocolNum = containerId.split('_')[1];
    procolDates[protocolNum] = date;
  });
  return procolDates;
}

/**
 * Sets the range of the dual range slider to number of months between minDate and maxDate
 */
function setMonthSliderRange(fromSlider, toSlider, minDate, maxDate, fromLabel, toLabel) {
  const monthCount = (maxDate.getFullYear() - minDate.getFullYear()) * 12 + (maxDate.getMonth() - minDate.getMonth());
  fromSlider.max = monthCount;
  toSlider.max = monthCount;
  fromSlider.value = 0;
  toSlider.value = monthCount;
  const [fromDate, toDate] = getSelectedDateRange(fromSlider, toSlider, minDate);
  fromLabel.innerText = serializeDate(fromDate);
  toLabel.innerText = serializeDate(toDate);
}

const formatter = new Intl.DateTimeFormat('de', { month: 'short' });

/**
 * @returns a Year Month string representation of the given date
 */
function serializeDate(date) {
  const month = formatter.format(date);
  const year = date.getFullYear();
  return `${month} ${year}`;
}

/**
 * @returns the date range selected by the dual range slider
 */
function getSelectedDateRange(fromSlider, toSlider, minDate) {
  const fromMonth = new Date(minDate.getFullYear(), minDate.getMonth() + parseInt(fromSlider.value));
  const toMonth = new Date(minDate.getFullYear(), minDate.getMonth() + parseInt(toSlider.value) + 1);
  return [fromMonth, toMonth];
}

/**
 * Updates protocol timeline to only show protocols within the selected date range
 * TODO: batch update dom with fragment to improve performance?
 */
function updateProtocolFilter() {
  const [fromDate, toDate] = getSelectedDateRange(fromSlider, toSlider, minDate);
  
  Object.entries(protocolDates).forEach(entry => {
    const [index, date] = entry;
    const container = document.querySelector(`#protocol_${index}`);    
    
    if (date >= fromDate && date <= toDate) {
      container.style.display = 'block';
    } else {
      container.style.display = 'none';
    }
  });
}

const protocolDates = findProtocolDates();
const dates = Object.values(protocolDates);
const minDate = new Date(Math.min(...dates));
const maxDate = new Date(Math.max(...dates));
const monthCount = (maxDate.getFullYear() - minDate.getFullYear()) * 12 + (maxDate.getMonth() - minDate.getMonth());

const fromSlider = document.querySelector('#fromSlider');
const toSlider = document.querySelector('#toSlider');
const fromLabel = document.querySelector('#fromLabel');
const toLabel = document.querySelector('#toLabel');

setMonthSliderRange(fromSlider, toSlider, minDate, maxDate, fromLabel, toLabel);  
fillSlider(fromSlider, toSlider, toSlider);
setToggleAccessible(toSlider);

fromSlider.oninput = () => controlFromSlider(fromSlider, toSlider, fromLabel, minDate);
toSlider.oninput = () => controlToSlider(fromSlider, toSlider, toLabel, minDate);
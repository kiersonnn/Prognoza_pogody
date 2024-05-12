import React, { useState } from 'react';
import { Helmet } from 'react-helmet';
import './App.css';

interface WeatherResponse {
  date: string;
  max_temperature: number;
  min_temperature: number;
  daylight_duration: number;
}

interface EnergyResponse {
  day: number;
  daylight_exposure: number;
  energy_generated: number;
}

const App: React.FC = () => {
  const [weatherData, setWeatherData] = useState<Record<string, WeatherResponse>>({});
  const [energyData, setEnergyData] = useState<Record<string, EnergyResponse>>({});
  const [darkMode, setDarkMode] = useState(false);
  const [latitude, setLatitude] = useState('21.2123');
  const [longitude, setLongitude] = useState('32.3123');

  const fetchWeather = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:4000/weather?latitude=${latitude}&longitude=${longitude}`);
      const data: Record<string, WeatherResponse> = await response.json();
      setWeatherData(data);
    } catch (error) {
      console.error('Error fetching weather data:', error);
    }
  };

  const fetchEnergy = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:4000/energy?latitude=${latitude}&longitude=${longitude}`);
      const data: Record<string, EnergyResponse> = await response.json();
      setEnergyData(data);
    } catch (error) {
      console.error('Error fetching energy data:', error);
    }
  };

  const loadData = () => {
    fetchWeather();
    fetchEnergy();
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const getLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        setLatitude(position.coords.latitude.toString().replace(',', '.'));
        setLongitude(position.coords.longitude.toString().replace(',', '.'));
      });
    } else {
      console.error("Geolocation is not supported by this browser.");
    }
  };

  return (
    <div className={`App ${darkMode ? 'dark-mode' : ''}`}>
      <Helmet bodyAttributes={{class: darkMode ? 'dark-mode' : ''}} />
      <button className="dark-mode-button" onClick={toggleDarkMode}>Toggle Dark Mode</button>
      <button onClick={getLocation}>Użyj mojej lokalizacji</button>
      <input type="text" value={latitude} onChange={e => setLatitude(e.target.value.replace(',', '.'))} placeholder="Latitude" />
      <input type="text" value={longitude} onChange={e => setLongitude(e.target.value.replace(',', '.'))} placeholder="Longitude" />
      <button onClick={loadData}>Załaduj dane</button>
      <h1>Weather Forecast</h1>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Max Temperature</th>
              <th>Min Temperature</th>
              <th>Daylight Duration</th>
              <th>Energy Generated</th>
            </tr>
          </thead>
          <tbody>
            {Object.keys(weatherData).map((date, index) => {
              const weather = weatherData[date];
              const energy = energyData[date];
              return (
                <tr key={index}>
                  <td>{date}</td>
                  <td>{weather.max_temperature}</td>
                  <td>{weather.min_temperature}</td>
                  <td>{weather.daylight_duration}</td>
                  <td>{energy ? energy.energy_generated : 'No data'}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default App;

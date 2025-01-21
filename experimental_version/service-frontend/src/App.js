import React, { useEffect, useState } from "react";
import axios from "axios";

function App() {
  // Створення стану для зберігання послуг
  const [services, setServices] = useState([]);

  // Функція для отримання даних з бекенда
  const fetchServices = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/services");
      setServices(response.data); // Зберігаємо дані в стані
    } catch (error) {
      console.error("Помилка при отриманні даних:", error);
    }
  };

  // Викликаємо fetchServices при завантаженні компонента
  useEffect(() => {
    fetchServices();
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>Список послуг</h1>
      <div>
        {services.map((service) => (
          <div
            key={service.service_id}
            style={{
              border: "1px solid #ddd",
              borderRadius: "8px",
              padding: "15px",
              margin: "10px 0",
            }}
          >
            <h2>{service.service_name}</h2>
            <p>
              <strong>Ціна:</strong> {service.service_price}
            </p>
            <p>
              <strong>Опис:</strong> {service.service_p}
            </p>
            <a href={service.service_url} target="_blank" rel="noopener noreferrer">
              Перейти на сайт
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;

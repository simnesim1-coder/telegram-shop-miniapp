import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export default function App() {
  const [page, setPage] = useState('catalog');
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [telegramId, setTelegramId] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
      const user = window.Telegram.WebApp.initDataUnsafe?.user;
      if (user) {
        setTelegramId(user.id);
      }
    }

    loadProducts();
    if (telegramId) {
      loadCart();
    }
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/products`);
      setProducts(response.data);
    } catch (error) {
      console.error('Ошибка загрузки товаров:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCart = async () => {
    if (!telegramId) return;
    try {
      const response = await axios.get(`${API_URL}/cart?telegram_id=${telegramId}`);
      setCart(response.data.items || []);
    } catch (error) {
      console.error('Ошибка загрузки корзины:', error);
    }
  };

  const addToCart = async (productId) => {
    if (!telegramId) {
      alert('Требуется авторизация');
      return;
    }
    try {
      await axios.post(`${API_URL}/cart?telegram_id=${telegramId}&product_id=${productId}`);
      loadCart();
      alert('✅ Добавлено в корзину');
    } catch (error) {
      console.error('Ошибка добавления в корзину:', error);
      alert('❌ Ошибка');
    }
  };

  const removeFromCart = async (itemId) => {
    try {
      await axios.delete(`${API_URL}/cart/items/${itemId}`);
      loadCart();
    } catch (error) {
      console.error('Ошибка удаления из корзины:', error);
    }
  };

  const checkout = async () => {
    if (!telegramId) return;
    try {
      const response = await axios.post(`${API_URL}/orders?telegram_id=${telegramId}`, {
        name: 'Клиент',
        phone: '+7 (900) 000-00-00',
        delivery_address: 'Москва',
        comment: 'Спешу!'
      });
      alert('✅ Заказ создан!');
      setCart([]);
      setPage('catalog');
    } catch (error) {
      console.error('Ошибка создания заказа:', error);
      alert('❌ Ошибка');
    }
  };

  const getTotalPrice = () => {
    return cart.reduce((sum, item) => {
      const product = products.find(p => p.id === item.product_id);
      return sum + (product?.price || 0) * item.quantity;
    }, 0);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🛍️ Магазин</h1>
        <nav className="nav">
          <button onClick={() => setPage('catalog')} className={page === 'catalog' ? 'active' : ''}>
            Каталог
          </button>
          <button onClick={() => setPage('cart')} className={page === 'cart' ? 'active' : ''}>
            🛒 Корзина ({cart.length})
          </button>
        </nav>
      </header>

      <main className="main">
        {page === 'catalog' && (
          <div className="catalog">
            <h2>Все товары</h2>
            {loading ? (
              <p>⏳ Загрузка...</p>
            ) : (
              <div className="products-grid">
                {products.map(product => (
                  <div key={product.id} className="product-card">
                    <div className="product-image">
                      {product.images?.[0]?.image_url ? (
                        <img src={product.images[0].image_url} alt={product.name} />
                      ) : (
                        <div className="no-image">🎁</div>
                      )}
                    </div>
                    <h3>{product.name}</h3>
                    <p className="description">{product.description}</p>
                    <div className="product-footer">
                      <span className="price">{product.price}р</span>
                      <button onClick={() => addToCart(product.id)} className="btn btn-primary">
                        В корзину
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {page === 'cart' && (
          <div className="cart">
            <h2>Корзина</h2>
            {cart.length === 0 ? (
              <p className="empty-cart">🛒 Корзина пуста</p>
            ) : (
              <>
                <div className="cart-items">
                  {cart.map(item => {
                    const product = products.find(p => p.id === item.product_id);
                    return (
                      <div key={item.id} className="cart-item">
                        <div className="item-info">
                          <h4>{product?.name}</h4>
                          <p>Кол-во: {item.quantity}</p>
                          <p className="price">{(product?.price || 0) * item.quantity}р</p>
                        </div>
                        <button 
                          onClick={() => removeFromCart(item.id)}
                          className="btn btn-danger btn-small"
                        >
                          🗑️
                        </button>
                      </div>
                    );
                  })}
                </div>
                <div className="cart-total">
                  <h3>Итого: {getTotalPrice()}р</h3>
                  <button onClick={checkout} className="btn btn-success">
                    ✅ Оформить заказ
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

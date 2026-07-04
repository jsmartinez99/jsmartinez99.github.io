/**
 * contact.js — Validación y feedback del formulario de contacto
 * Integración con Formspree (sin backend propio)
 */
(function() {
  'use strict';

  const form = document.getElementById('contact-form');
  if (!form) return;

  const feedback = document.getElementById('form-feedback');
  const submitBtn = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Validación client-side
    const nombre = form.querySelector('[name="name"]').value.trim();
    const email = form.querySelector('[name="email"]').value.trim();
    const message = form.querySelector('[name="message"]').value.trim();

    if (!nombre || !email || !message) {
      showFeedback('error', 'Todos los campos son obligatorios.');
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      showFeedback('error', 'Por favor, ingresá un email válido.');
      return;
    }

    // Estado: enviando
    setSending(true);

    try {
      const resp = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'Accept': 'application/json' }
      });

      if (resp.ok) {
        showFeedback('success', '¡Mensaje enviado con éxito! Te responderé a la brevedad.');
        form.reset();
      } else {
        const data = await resp.json();
        showFeedback('error', data.error || 'Error al enviar. Intentá de nuevo.');
      }
    } catch (err) {
      showFeedback('error', 'Error de conexión. Verificá tu internet y volvé a intentar.');
    } finally {
      setSending(false);
    }
  });

  function setSending(sending) {
    if (!submitBtn) return;
    submitBtn.disabled = sending;
    submitBtn.innerHTML = sending
      ? '<span class="spinner"></span> Enviando...'
      : 'Enviar mensaje';
  }

  function showFeedback(type, message) {
    if (!feedback) return;
    feedback.className = 'form-feedback form-feedback--' + type;
    feedback.textContent = message;
    feedback.style.display = 'block';
    // Auto-ocultar después de 5 segundos
    setTimeout(() => { feedback.style.display = 'none'; }, 5000);
  }
})();

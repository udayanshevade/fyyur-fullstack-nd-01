(() => {
  /**
   * Handles delete button click for a venue
   * @param {Event} e
   */
  const handleDeleteVenue = async (e) => {
    const id = e.target.dataset.venueId;
    try {
      const res = await fetch(`/venues/${id}`, { method: 'delete' });
      const val = await res.json();
      if (val) {
        window.location.replace('/venues');
      } else {
        // replace with better error handling
        alert('Failed to delete the venue. Try again later.');
      }
    } catch (err) {
      console.error(err);
    }
    return false;
  };

  const btn = document.getElementById('btnDeleteVenue');
  btn.addEventListener('click', handleDeleteVenue);
})();

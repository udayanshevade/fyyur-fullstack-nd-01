(() => {
  /**
   * Handles delete button click for an artist
   * @param {Event} e
   */
  const handleDeleteArtist = async (e) => {
    const id = e.target.dataset.artistId;
    try {
      const res = await fetch(`/artists/${id}`, { method: 'delete' });
      const val = await res.json();
      if (val) {
        window.location.replace('/artists');
      } else {
        // replace with better error handling
        alert('Failed to delete the artist. Try again later.');
      }
    } catch (err) {
      console.error(err);
    }
    return false;
  };

  const btn = document.getElementById('btnDeleteArtist');
  btn.addEventListener('click', handleDeleteArtist);
})();

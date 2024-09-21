// script.js

document.addEventListener('DOMContentLoaded', function() {
    // Disable prompt input and show spinner on form submit
    document.getElementById('prompt-form').addEventListener('submit', function() {
        // Hide the submit icon
        document.getElementById('submit-icon').style.display = 'none';
        // Show the spinner
        document.getElementById('spinner').style.display = 'inline-block';
        // Disable the prompt input field
        document.getElementById('prompt-input').readOnly = true;
    });

    // Rating functionality
    var starsElement = document.getElementById('stars');
    if (starsElement) {
        var videoName = starsElement.getAttribute('data-video');

        document.querySelectorAll('.star').forEach(function(star) {
            star.addEventListener('click', function() {
                var rating = this.getAttribute('data-value');

                // Send the rating to the server
                fetch('/rate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                    },
                    body: JSON.stringify({
                        'video_name': videoName,
                        'rating': rating
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status == 'success') {
                        // Update the average rating display
                        document.getElementById('average-rating').innerText = 'Average Rating: ' + data.average_rating.toFixed(2) + ', Number of Ratings: ' + data.number_of_ratings;
                        //alert('Thank you for your rating!');

                        // Update the star display
                        var ratingValue = parseInt(rating);
                        document.querySelectorAll('.star').forEach(function(s) {
                            var starValue = parseInt(s.getAttribute('data-value'));
                            if (starValue <= ratingValue) {
                                s.classList.add('selected');
                            } else {
                                s.classList.remove('selected');
                            }
                        });
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            });
        });
    }
});


// script.js

document.addEventListener('DOMContentLoaded', function() {
    // Existing code...

    // Modal functionality
    var videoListButton = document.getElementById('video-list-button');
    var modal = document.getElementById('video-list-modal');
    var closeButton = document.querySelector('.close-button');

    videoListButton.addEventListener('click', function() {
        modal.style.display = 'block';
    });

    closeButton.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });

    // Filtering the video list
    var videoSearchInput = document.getElementById('video-search-input');

    videoSearchInput.addEventListener('input', function() {
        var filter = this.value.toLowerCase();
        var videoItems = document.querySelectorAll('.video-item');

        videoItems.forEach(function(item) {
            var text = item.textContent.toLowerCase();
            if (text.includes(filter)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    });

    // Navigate to selected video
    document.querySelectorAll('.video-item').forEach(function(item) {
        item.addEventListener('click', function() {
            var videoName = this.getAttribute('data-video-name');
            window.location.href = '/?video_name=' + encodeURIComponent(videoName);
        });
    });
});


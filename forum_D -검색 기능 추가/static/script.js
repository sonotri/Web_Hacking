document.addEventListener("DOMContentLoaded", () => {
  const postForm = document.getElementById("post-form");
  const postList = document.getElementById("post-list");

  // Sample data to visualize posts
  const posts = [
    { id: 1, title: "First Post", content: "This is the first post content." },
    {
      id: 2,
      title: "Second Post",
      content: "This is the second post content.",
    },
  ];

  // Function to display posts
  function displayPosts() {
    postList.innerHTML = "";
    posts.forEach((post) => {
      const postItem = document.createElement("div");
      postItem.classList.add("post-item");
      postItem.innerHTML = `
                <div class="post-title">${post.title}</div>
                <div class="post-content">${post.content}</div>
            `;
      postList.appendChild(postItem);
    });
  }

  // Add new post
  postForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const title = document.getElementById("title").value;
    const content = document.getElementById("content").value;

    // Here you would typically send the data to the backend
    posts.push({ id: posts.length + 1, title, content });
    displayPosts();
    postForm.reset();
  });

  // Initial display of posts
  displayPosts();
});

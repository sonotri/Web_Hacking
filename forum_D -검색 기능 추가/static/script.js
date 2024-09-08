document.addEventListener("DOMContentLoaded", () => {
  const postForm = document.getElementById("post-form");
  const postList = document.getElementById("post-list");

  // 시각화
  const posts = [
    { id: 1, title: "First Post", content: "This is the first post content." },
    {
      id: 2,
      title: "Second Post",
      content: "This is the second post content.",
    },
  ];

  //----------------------
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

  // 새로운 게시글을 올리는
  postForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const title = document.getElementById("title").value;
    const content = document.getElementById("content").value;

    posts.push({ id: posts.length + 1, title, content });
    displayPosts();
    postForm.reset();
  });

  //페이지를 처음 열 때 초기 게시물 상태를 표시한다.
  displayPosts();
});

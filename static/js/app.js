async function loadFiles(path = "") {
  const res = await fetch("/api/list?path=" + encodeURIComponent(path));
  const data = await res.json();
  const fileList = document.getElementById("fileList");
  fileList.innerHTML = "";
  data.items.forEach(item => {
    const li = document.createElement("li");
    const left = document.createElement("div");
    left.textContent = item.is_dir ? `📁 ${item.name}` : `📄 ${item.name}`;

    const right = document.createElement("div");
    if(item.is_dir){
      const btn = document.createElement('button');
      btn.textContent = 'Open';
      btn.onclick = () => { loadFiles(path ? `${path}/${item.name}` : item.name); };
      right.appendChild(btn);
    } else {
      const a = document.createElement('a');
      a.href = path ? `/download/${encodeURIComponent(path + '/' + item.name)}` : `/download/${encodeURIComponent(item.name)}`;
      a.textContent = 'Download';
      right.appendChild(a);
    }

    li.appendChild(left);
    li.appendChild(right);
    fileList.appendChild(li);
  });

  const bc = document.getElementById("breadcrumb");
  bc.innerHTML = "";
  let parts = path.split("/").filter(Boolean);
  let accum = "";
  const rootLink = document.createElement("a");
  rootLink.href = "#";
  rootLink.textContent = "Home";
  rootLink.onclick = () => { loadFiles(""); return false; };
  bc.appendChild(rootLink);
  parts.forEach(p => {
    bc.append(" / ");
    accum += "/" + p;
    const l = document.createElement("a");
    l.href = "#";
    l.textContent = p;
    l.onclick = () => { loadFiles(accum); return false; };
    bc.appendChild(l);
  });

  document.getElementById("uploadPath").value = path;
}

document.getElementById("uploadForm").addEventListener("submit", async e => {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const res = await fetch("/upload", { method: "POST", body: formData });
  document.getElementById("uploadStatus").textContent = res.ok ? "Upload successful" : "Upload failed";
  form.reset();
  loadFiles(formData.get("path"));
});

window.onload = () => {
  loadFiles("");
};

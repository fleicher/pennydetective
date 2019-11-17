<template>
  <div class="hello">
    <h1>S3 Uploader Test</h1>

    <div v-if="!image">
      <h2>Select an image</h2>
      <input type="file" @change="onFileChange">
    </div>
    <div v-else>
      <img :src="image" alt="image_to_upload"/>
      <button v-if="!uploadURL" @click="removeImage">Remove image</button>
      <button v-if="!uploadURL" @click="uploadImage">Upload image</button>
    </div>
    <h2 v-if="uploadURL">Success! Image uploaded to:</h2>
    <a :href="uploadURL">{{ uploadURL }}</a>
  </div>
</template>

<script>

import axios from 'axios'
const MAX_IMAGE_SIZE = 1000000;

export default {
  name: 's3uploader',
  data () {
    return {
      image: '',
      uploadURL: ''
    }
  },
  methods: {
    onFileChange (e) {
      let files = e.target.files || e.dataTransfer.files;
      if (!files.length) return;
      this.createImage(files[0])
    },
    createImage (file) {
      // var image = new Image()
      let reader = new FileReader();

      reader.onload = (e) => {
        console.log('is jpg?: ', e.target.result.includes('data:image/jpeg'));
        if (!e.target.result.includes('data:image/jpeg')) {
          return alert('Wrong file type - JPG only.')
        }
        if (e.target.result.length > MAX_IMAGE_SIZE) {
          return alert('Image is loo large - 1Mb maximum')
        }

        this.image = e.target.result
      };
      reader.readAsDataURL(file)
    },
    removeImage: function (e) {
      console.log('Remove clicked');
      this.image = ''
    },
    uploadImage: async function (e) {
      console.log('Upload clicked');
      const apiurl = `https://muz8yko9fj.execute-api.us-east-2.amazonaws.com/test/s3upload`;
      const response = await axios({
          method: 'POST',
          url: apiurl,
          data: {
              account: "0815",
              suffix: '.jpg',
              type: "image/jpeg",
              image: this.image.split(',')[1],
          },
          headers: { 'Content-Type': 'application/json' },
      });
      console.log('Response: ', response.data);
      // const data = JSON.parse(response.data);
      this.uploadURL = response.data.url
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
#app {
  text-align: center;
}
img {
  width: 30%;
  margin: auto;
  display: block;
  margin-bottom: 10px;
}
button {
}
</style>

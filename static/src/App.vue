<template>
  <div id="app">
    <div class="file-server">
      <div class="server-address">
        <span>服务器地址是：</span>
        <span>{{url}}</span>
        <div class="clear"></div>
      </div>
      <div class="server-qrcode" @click="showCode">
        <span>点击查看二维码</span>
        <span></span>
      </div>
      <div class="clear"></div>
    </div>
    <div id="popup" v-show="qrcodeShow">
      
    </div>
    <div class="file-list">
      <div class="list-top">共享文件列表</div>
      <div class="list-body">
        <div class="file-specifc" v-for="file in files">
          <span>{{file}}</span>
          <a target="_blank" :href="'http://localhost:5000/shared/' + file" class="download"></a>
          <span :filename="file" class="delete" @click="deleteFile($event)"></span>
        </div>
      </div>
    </div>
    <div class="upload">
      <div class="select">
        <input id="form" type="file" name="">
        <span class="cover">选择文件</span>
      </div>
      <button class="upload-file" @click="uploadFile">上传文件</button>
    </div>
  </div>
</template>

<script>
  import res from '../res.min.js'
  export default {
    name: 'app',
    data() {
     return {
        files: [],
        qrcodeShow: false,
        url: ''
     }
    },
    methods: {
      showCode () {
        this.$data.qrcodeShow = !this.$data.qrcodeShow
      },
      deleteFile (event) {
        let name = event.target.attributes.filename.value
        res.shared.delete({name: name})
          .then( data => {
            let index = this.files.indexOf(name)
            this.files.splice(index, 1)
          })
          .catch( err => {
            console.log(err)
            alert('删除文件不成功')
          })
      },
      uploadFile () {
        let upload = document.getElementById('form')
        let data = new FormData()
        if (upload.files.length === 0) {
          alert('您还没有选择文件')
        }
        for (let i in form.files) {
          data.append(i, form.files[i])
        }
        res.shared.post(data)
          .then ( data => {
            let result = data[0]
            result.saved ? this.$data.files.push(result.name) : alert('上传文件失败')
          })
      }
    },
    ready () {
      res.shared.get_server_address()
       .then( data => {
          this.$data.url = data.url
          new QRCode(document.getElementById('popup'), data.url)
        })
       .catch( err => {
          console.log(err)
       })
      res.shared.get_list()
        .then( data => {
          this.$data.files = data
        })
        .catch( err => {
          console.log(err)
        })
    }
  }
</script>

<style lang="scss">
  @mixin background($back: './assets/download.png') {
    background: url($back);
    background-size: 30px 30px;
    background-repeat: no-repeat;
    cursor: pointer;
    opacity: 0.6;
    background-position: center;
    &:hover {
      opacity: 1
    }
  }
  @mixin cheat($index: 1) {
    position: absolute;
    top: 0px;
    left: 0px;
    height: 30px;
    line-height: 30px;
    width: 100px;
    z-index: $index
  }
  html {
    height: 100%;
    #app {
      color: #2c3e50;
      width: 80%;
      margin: 10px auto;
      font-family: Source Sans Pro, Helvetica, sans-serif;
      text-align: center;
      .file-server {
        z-index: 1;
        span {
          height: 30px;
          line-height: 30px;
          display: block;
          float: left;
        }
        .server-address {
          float: left;
        }
        .server-qrcode {
          float: right;
          span {
            &:last-child {
              float: right;
              width: 30px;
              height: 30px;
              line-height: 30px;
              background-image: url('./assets/shrink.png');
              background-size: 27px 27px;
              text-align: center;
            }
          }
        }
      }
      #popup {
        width: 300px;
        height: 300px;
        z-index: 99;
        background: rgba(0,0,0,.2);
        position: absolute;
        left: 50%;
        top: 50%;
        margin-left: -150px;
        margin-top: -150px;
        img {
          width: 80%;
          margin-top: 10%;
          margin-left: 10%;
        }
      }
      .file-list {
        margin-top: 30px;
        .list-top {
          height: 45px;
          line-height: 45px;
          background: rgba(0,0,0,.3);
          border: 0.5px solid #ccc;
          border-radius: 3px;
          color: #fff;
          text-align: left;
          padding-left: 10px;
        }
        .list-body {
          .file-specifc {
            height: 40px;
            line-height: 40px;
            border-bottom: 0.5px solid rgba(44, 62, 80, .5);
            span {
              display: block;
              line-height: 40px;
              width: 25%;
              height: 40px;
              float: left;
              &:first-child {
                padding-left: 5px;
                width: 48%;
                text-align: left;
              }
            }
            .download {
              display: block;
              float: left;
              width: 25%;
              height: 40px;
              @include background;
            }
            .delete {
              @include background($back: './assets/delete.png')
            }
          }
        }
      }
      .upload {
        position: relative;
        height: 30px;
        width: 200px;
        margin-top: 30px;
        .select {
          float: left;
          width: 100px;
          input {
            @include cheat($index: 99);
            opacity: 0;
          }
          span {
            @include cheat;
            background: rgba(60,60,60,.7);
            border: 0px;
            color: #fff;
            border-radius: 3px;
            cursor: pointer;
          }
        }
        .upload-file {
          width: 80px;
          height: 30px;
          line-height: 30px;
          border: 0px;
          color: #fff;
          border-radius: 3px;
          background: #4078c0;
          float: right;
          cursor: pointer;
        }
      }
    }
    .clear {
      clear: both;
      width: 0px;
      height: 0px
    }
  }
</style>

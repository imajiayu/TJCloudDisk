<template>
	<div>
  <div id="dirmenu" v-show="DirMenuVisible" class="menu">
	<div class="contextmenu_item" @click="removeMenu();downloadFunc()">下载文件夹</div>
	<div class="contextmenu_item" @click="removeMenu();openSaveForm()">转存</div>
  
  </div>
  <div id="filemenu" v-show="FileMenuVisible" class="menu">
	<div class="contextmenu_item" @click="removeMenu();downloadFunc()">下载文件</div>
	<div class="contextmenu_item" @click="removeMenu();openSaveForm()">转存</div>
  </div>


	<el-dialog width="40%" v-model="this.saveForm.visible" title="转存到">
		<div class="el-dialog-div">
		<el-container>
			<el-main>
				<el-tree 
			ref="copyFileTree"
      class="file-tree"
      :data="fileTree" 
      node-key="id"
      empty-text=""
			:expand-on-click-node="false"
      @node-expand="(data,node,t)=>{data.isopen=true;}"
      @node-collapse="(data,node,t)=>{data.isopen=false;}">
		<template #default="{ node, data }">
		<span  class="custom-tree-node">
				<!--font-awesome-icon icon="fa-brands fa-java" /-->
					<el-icon v-if="data.children && data.isopen"><FolderOpened /></el-icon>
					<el-icon v-else-if="data.children && !data.isopen"><Folder/></el-icon>
					<el-icon v-else><Document /></el-icon>
				<i v-if="data.children && !data.isopen" class="el-icon-folder"></i>
				<i v-else-if="data.children && data.isopen" class="el-icon-folder-opened"></i>
				<i v-else class="el-icon-document"></i>
				<span>{{ node.label }}</span>
		</span>
		</template>
		</el-tree>
			</el-main>
			<el-footer>
				<span class="dialog-footer">
        <el-button @click="closeSaveForm()">取消</el-button>
        <el-button type="primary" @click="saveFunc()"
          >确认</el-button
        >
    		</span>
			</el-footer>
		</el-container>
		</div>

	</el-dialog>





	


		<el-container>
			<el-header style="border-bottom: solid rgba(219, 219, 219, 0.874);">
				<Header :avatar="imageUrl"></Header>
			</el-header>
					<el-container>
			<el-header height="15px" style="margin-top:10px">
        <div>



      
      <el-button 
        style="margin-left:5px" 
        @click="refreshPath()"
        circle>
        <el-icon><RefreshRight/></el-icon>
      </el-button>
      <el-button 
        style="margin-left:5px;margin-right:20px;" 
        @click="jumpPath(Math.max(this.path_list.length-2,0))"
        circle>
        <el-icon><ArrowLeft/></el-icon>
      </el-button>


          <!-- <div v-for="(path, index) in this.path_list" :key="index" style="display:inline;margin:0 5px;">
            <el-button type="text"	size="small" @click="jumpPath(index)">
              {{ path.name }}
            </el-button>
          </div> -->

						<el-button-group>
            <el-button 
						v-for="(path, index) in this.path_list" 
						:key="index" 
						type=""	
						size="default" 
						@click="jumpPath(index)">
              {{ path.name }}
            </el-button>
						</el-button-group>

        </div>
			</el-header>
			<el-main>
				<el-table
					:data="this.file_list"
					style="width: 100%"
					@row-contextmenu="rightClick"
				>
					<el-table-column
						label="名称"
						width="400"
					>
						<template #default="scope">
							<div>
								<el-icon><Folder v-if="scope.row.type=='dir'"/><Document v-else /></el-icon>
								<el-button
                  v-if="scope.row.type=='dir'"
									type="text"
									@click="jumpDir(scope.row.id,scope.row.name)"
								>
									{{ scope.row.name }}
								</el-button>
                <el-button
                  v-else
									type="text"
									@click="jumpFile(scope.row.id,scope.row.name)"
								>
									{{ scope.row.name }}
								</el-button>
							</div>
						</template>
					</el-table-column>
					<el-table-column
						prop="lastchange"
						label="修改日期"
						width="180"
					/>
					<el-table-column
						label="大小"
					>
					<template #default="scope">
							<div>
								<span
                  v-if="scope.row.type=='dir'"
								>
									-
								</span>
								<span v-else>
									{{ scope.row.fsize>1024*1024?(scope.row.fsize/1024/1024).toFixed(2)+'MB':scope.row.fsize>1024?(scope.row.fsize/1024).toFixed(2)+'KB':scope.row.fsize.toString()+'B' }}
								</span>
							</div>
						</template>
					</el-table-column>
				</el-table>
				
			</el-main>
		</el-container>
		</el-container>



	</div>
</template>
  
<script >
import Header from '../components/Header.vue'
import { ElMessage,ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { WarningFilled } from '@element-plus/icons-vue'
import { CirclePlus, Plus, Minus, FolderAdd,Upload,RefreshRight,ArrowLeft,Folder,FolderOpened,Document } from '@element-plus/icons-vue'
import { reactive, toRefs } from 'vue'
import { Check } from '@element-plus/icons-vue'
import Cookies from 'js-cookie'
import SparkMD5 from 'spark-md5'


let uploadParam={
	pid:0,
	axios:null,
}

export default {
	components: {
		Minus,
		Plus,
		Check,
		FolderAdd,
    Upload,
    RefreshRight,
    ArrowLeft,
		reactive,
		toRefs,
		CirclePlus,
		WarningFilled,
		ArrowDown,
		ElMessageBox,
    ElMessage,
		Header,
		Folder,
		FolderOpened,
		Document,
	},
	el: '#app',
	name: 'userspace',
	data() {
		return {
			uid: '',
			email: '132',
			Username: '',

			imageUrl: '',
			file_list: [],
      path_list: [],
      newDirForm:{
        visible:false,
        name:'',
      },
      uploadForm:{
        visible :false,
        name:'',
        fileList: [],
      },
			renameForm:{
        visible :false,
        name:'',
      },
			saveForm:{
        visible :false,
      },
			moveForm:{
        visible :false,
      },
			shareForm:{
        visible :false,
				shareURL: null,
      },
			uploadURL: '',
			DirMenuVisible: false,
			FileMenuVisible: false,
			selectRow: null,
			fileTree: [],
			selectNode: null,
			shareClipboard: null,
		}
	},
	created() {
		console.log(this.$route.params.token);

		this.axios.get('/api/accounts/myinfo/', {}).then((response) => {
			this.email = response.data.data.email
			this.uid = response.data.data.uid
			this.imageUrl =
				'/static/avatar/' + this.uid + '.jpg' + `?${Date.now()}`
		})
		this.axios.get('/api/share/verifysharetoken/?token='+this.$route.params.token,{})
		.then((response)=>{
			console.log(response);
			this.file_list = response.data.data;
			this.path_list=[{name:"share/",id:-1}]
		})
		.catch((e)=>{
			console.log(e.response);
			if(e.response.status==400){
				ElMessage.error(e.response.data.data.detail)
				this.$router.push({ name: 'UserSpace' })
			}
			else if(e.response.status==401){
				ElMessage.error(e.response.data.data.detail)
				this.$router.push({ name: 'UserSpace' })
			}
		})
		// this.axios.get('/api/filesystem/getroot', {}).then((response) => {
		// 	console.log(response)
		// 	this.file_list = response.data.data
    //   this.path_list=[{name:"root/",id:response.data.rootid}]
		// })
	},
	methods: {
		forId: function (index) {
			return index
		},
		jumpHome: function (param1) {
			let number = param1
			let pid = this.project_list[number]['pid']
			Cookies.set('uid', this.uid)

			this.$router.push({ name: 'Home', query: { pid: pid } })
		},
    jumpPath: function (index) {
      console.log(index);
			if(index==0){
				this.axios.get('/api/share/verifysharetoken/?token='+this.$route.params.token,{})
				.then((response)=>{
					console.log(response);
					this.file_list = response.data.data;
					this.path_list=[{name:"share/",id:-1}]
				})
				.catch((e)=>{
					console.log(e.response);
					if(e.response.status==400){
						ElMessage.error(e.response.data.data.detail)
						this.$router.push({ name: 'UserSpace' })
					}
					else if(e.response.status==401){
						ElMessage.error(e.response.data.data.detail)
						this.$router.push({ name: 'UserSpace' })
					}
				})
			}
			else{
				this.axios.get('/api/filesystem/getdir/?pid='+this.path_list[index].id, {}).then((response) => {
					console.log(response)
					this.file_list = response.data.data
					while(this.path_list.length!=index+1){
						this.path_list.pop();
					}        
				}); 
			}
 
    },
		jumpDir: function (id, name) {
			console.log(id, name)
      this.axios.get('/api/filesystem/getdir/?pid='+id, {}).then((response) => {
        console.log(response)
        this.file_list = response.data.data
        this.path_list.push({name:name+'/',id:id});
      });      
		},
    refreshPath: function (){
      this.jumpPath(this.path_list.length-1);
    },

		

		rightClick: function (row, column, event) {
				// console.log(row, column, event)
				this.selectRow=row;
				event.preventDefault();
				this.removeMenu();
				let menu;
				if(row.type=='dir'){
					menu=document.querySelector("#dirmenu");
					this.DirMenuVisible=true;
				}
				else if(row.type=='file'){
					menu=document.querySelector("#filemenu");
					this.FileMenuVisible=true;
				}
				this.styleMenu(event,menu);
    },
    removeMenu: function () {
        // 取消鼠标监听事件 菜单栏
        // console.log('removeTreeMenu')
        this.DirMenuVisible = false;
        this.FileMenuVisible = false;
        document.removeEventListener("click", this.removeMenu); // 关掉监听，
    },
    styleMenu: function (key, menu) {        
        document.addEventListener("click", this.removeMenu); // 给整个document新增监听鼠标事件，点击任何位置执行foo方法            
        menu.style.left = key.pageX  + "px";
        menu.style.top = key.pageY  + "px";
        //console.log('for menu style',menu.style.left,menu.style.top);
    },
		downloadFunc: function () {
			console.log(this.selectRow);
			let row=this.selectRow;
			let URL=row.type=='file'?'/api/transfer/downloadfile?fid='+row.id:'/api/transfer/downloaddir?did='+row.id;
			this.axios.get(URL, {responseType: "blob"}).then((response) => {
        let blob = new Blob([response.data])

        const utf8FilenameRegex = /filename\*=utf-8''([\w%\-.]+)(?:; ?|$)/i;
        const asciiFilenameRegex = /filename=(["']?)(.*?[^\\])\1(?:; ?|$)/i;
        
        let filename = 'download'
        const fileName = response.headers['content-disposition'];
        const utf8filename = utf8FilenameRegex.exec(fileName)
        const asciifilename = asciiFilenameRegex.exec(fileName)
        if (utf8filename)
          filename = utf8filename[1]
        else 
          filename = asciifilename[2] 

        console.log(fileName)
				console.log(filename)
        let dom = document.createElement('a')
        let url = window.URL.createObjectURL(blob)
        dom.href = url
        dom.download = decodeURI(filename)
        
        dom.style.display = 'none'
        document.body.appendChild(dom)
        dom.click()
        dom.parentNode.removeChild(dom)
        window.URL.revokeObjectURL(url)
        ElMessage.success(row.name+'下载成功!');  
      });  
		},


		openSaveForm: function(){
			this.axios.get("/api/share/getdirtree/",{}).then((response)=>{
				console.log(response);
				this.fileTree=response.data.data;
				this.saveForm.visible=true;
			})
		},
		closeSaveForm: function(){
			this.saveForm.visible=false;			
			this.fileTree=[];
		},

		saveFunc: function (){
			let row=this.selectRow;
			let node=this.$refs.copyFileTree.getCurrentNode();
			let URL=row.type=='file'?'/api/share/copyfile/':'/api/share/copydir/';
			let content=row.type=='file'?{fid:row.id,pid:node.did}:{did:row.id,pid:node.did};
			console.log(node);
			this.axios.post(URL, content)
			.then((response) => {
        console.log(response);
        ElMessage.success(row.name+'转存成功!');  
				this.refreshPath();
				this.closeSaveForm();
      })
			.catch((e)=>{
				console.log(e)
				ElMessage.error(e.response.data.data.detail+"，已返回个人空间")
			});  	

		},







	},
}
</script>
 
<style scoped>
.box {
	display: flex;
	flex-direction: column;
	justify-content: space-between;
	align-items: center;
}
.el-collapse {
	margin-right: 50px;
	margin-left: 50px;
}
.el-descriptions {
	margin-top: 20px;
	margin-right: 70px;
	margin-left: 70px;
}
/deep/ .el-collapse-item__header {
	font-size: 20px;
}
.el-carousel__item h3 {
	display: flex;
	color: #475669;
	opacity: 0.75;
	line-height: 300px;
	margin: 0;
}

.el-carousel__item:nth-child(2n) {
	background-color: #99a9bf;
}

.el-carousel__item:nth-child(2n + 1) {
	background-color: #d3dce6;
}

.menu {
  position: absolute;
  background-color: #fff;
  width: 100px;
  /*height: 106px;*/
  font-size: 12px;
  color: #444040;
  border-radius: 4px;
  -webkit-box-sizing: border-box;
  box-sizing: border-box;
  border-radius: 3px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.175);
  white-space: nowrap;
  z-index: 1000;
}
.contextmenu_item {
  display: block;
  line-height: 34px;
  text-align: center;
}
.contextmenu_item:not(:last-child) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}
.contextmenu_item:hover {
  cursor: pointer;
  background: #66b1ff;
  border-color: #66b1ff;
  color: #fff;
}

.el-container{

        height:100%;

}

.el-tree {
     display: inline-block;
      .el-tree-node {
        > .el-tree-node__children {
          overflow: unset;
        }
     }
}

.el-dialog-div{
    height: 50vh;
     overflow: auto;
    }
.el-dialog-div-share{
    height: 20vh;
     overflow: auto;
    }


</style>  
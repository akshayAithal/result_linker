import { Button } from 'antd'; // Button = antd.Button
import { Col } from 'antd';
import { Row } from 'antd';
import { Tabs } from 'antd';
import { Icon } from 'antd';
import { Layout } from 'antd';
import { Menu, Dropdown } from 'antd';
import { Popover } from 'antd';
import { Form } from 'antd';
import { notification } from 'antd';
import { Input } from 'antd';
import { InputNumber } from 'antd';
import { Modal } from 'antd';
const { Header, Content } = Layout;
const { TabPane } = Tabs;
import { Alert } from 'antd';
import { Select } from 'antd';
import { Progress } from 'antd';
import { message } from 'antd';
import { Spin } from 'antd';
import axios from 'axios';
import {UploadOutlined } from '@ant-design/icons';
import 'intro.js/introjs.css';
import 'intro.js/themes/introjs-modern.css';
var introJs = require("intro.js");

import { LoginPage } from './loginpage';
import { PartTree } from './parttree';
import { ResultLinkerFooter } from './footer';
import { DataUploadPage } from './datauploadpage';
const { Option } = Select;
import React from 'react';
import FileSaver from 'file-saver';

import newId from './newid';

//const OnSelectAll = (e) =>
//{
//    console.log("Select All")
//}
//const Popup = ({visible, x, y}) => visible &&
//  <ul className="popup" style={{left: `${x}px`, top: `${y}px`}}>
//    <li }><Icon type="select"/>Select All</li>
//    <li><Icon type="carry-out"/>Select only public</li>
//    <li><Icon type="small-dash"/>Unselect All</li>
//  </ul>

let timer = 0;
let delay = 200;
let prevent = false;

const axiosInstance = axios.create({
    baseURL: window.location.href ,
    //proxy: true
  });

export class Body extends React.Component {
    constructor(props) {
        super(props);
        //var query = window.location.search.substring(1);
        //var pair = query.split("=");
        var issue_id = null
        //if (pair && pair.length==2)
        //{ 
        //    issue_id = pair[1]
        //}
        var intervalProgressLoop = null;
        var revisionState = null
        var allow_revisions = null
        axiosInstance.get("/check_login")
            .then(res => {
                const isLoggedIn = res.data.success;
                const userName = res.data.username;
                //For testing 
                const guestUser = res.data.guest;//false;
                const allowRevision = res.data.allow_revisions;//false;
                const root_folder = res.data.root_folder;//false;
                //console.log(res.data)
                if(res.data.issue_id)
                {
                    issue_id = res.data.issue_id.toString()
                }
                if(res.data.revision)
                {
                    revisionState = res.data.revision
                }
                this.setState({ isLoggedIn, 
                    userName ,
                    guestUser, 
                    ticket_id :issue_id,
                    currentRevision:revisionState,
                    allowRevision
                })
                if(issue_id)
                    this.populateProducts()
                else if (guestUser){
                    this.setState({ mode: "repo_explorer", revisions:[], expandedKeys:[], ticket_id:"", loadedKeys: []});
                    this.populateProductsforFolder(root_folder)
                }
                this.render()
            })
            .catch(error => {
                //console.log(error);
                const isLoggedIn = false;
                const guestUser = false;
                this.setState({ isLoggedIn, userName:null, guestUser})
            })
            //console.log(issue_id);
            this.state = {
                folders: [],
                currentPage: '1',
                roots: [],
                folderNamesCache: {},
                selectedKeys: null,
                expandedKeys: [],
                autoExpandParent: true,
                selected: null,
                ticket_id: issue_id,
                checkedKeys: [],
                checked_nodes: [],    //Now Defunct
                loading: false,
                iconLoading: false,
                iconBrowseLoading: false,
                iconLoadingGoUp:false,
                currentRevision:"",
                loadedKeys: [],
                currentProgress: 0,
                progressBarVisible: false,
                progressBarKey:"",
                mode:"normal",
                folderList:[],
                public_folders_only:[],
                modalVisible: false,
                current_path_to_commit: null,
                allowRevision: false,
                revisions:[],
                rightClickElement:null,
                revisionLoading:false,
                allow_ticket_related_operations: true,
       }
    }

    onCheck(checkedKeys,e) {
        console.log('onCheck', checkedKeys);
        //const checked_nodes = e.checkedNodes
        //this.setState({ checked_nodes });
        this.setState({ checkedKeys });
       

      };

      doDoubleClickAction(e,info) {
        var selectedNode = null
        if(!info.props || !info.props.dataRef)
        {
            return
        }
        selectedNode = info.props.dataRef
        console.log(selectedNode)
        if(selectedNode && selectedNode.isNode)
        {
            this.setState({expandedKeys:[...this.state.expandedKeys,selectedNode.id]})
            return
        }
        else if (selectedNode){
            //To be moved into a function
            const timestamp = Date.now();
            var fromattedTimestamp = new Intl.DateTimeFormat('en-US', {year: 'numeric', month: '2-digit',day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit'}).format(timestamp)
            fromattedTimestamp = fromattedTimestamp.split("/").join("_")
            fromattedTimestamp = fromattedTimestamp.split(":").join("_")
            fromattedTimestamp = fromattedTimestamp.split(" ").join("_")
            fromattedTimestamp = fromattedTimestamp.split(",").join("")
            let payload = {
                issue_id:this.state.ticket_id,
                data: [selectedNode],
                time_stamp:fromattedTimestamp,
                revision:this.state.currentRevision
              };
            
            axiosInstance.post('/download/open/',payload )
            .then(response => {
                let win = window.open(response.data.exported_file_path, '_blank');
                win.focus();
              }).catch((response) => {
                console.error("Could not Download the data from the backend.", response);
              })
        }
        
      }
    
    handleSelect(node) {
        const selectedKeys = node
        this.setState({selectedKeys});
        //if (this.state.mode === "repo_browser")
        //{
        //    this.get_revisions(selectedKeys)
        //}
    }
    onTreeExpand(expandedKeys) {
        this.setState({expandedKeys, autoExpandParent: false});
    }
    onVisibleChangeOfRightClick()
    {

        if(this.state.rightClickElement)
        {
            this.setState({rightClickElement:null})
        }
    }
    onRightClick(e)
    {
        this.setState({rightClickElement:e.node})
    }

    onClickGoUp(e)
    {
        if(!this.state.iconLoadingGoUp)
        {
            this.setState({ iconLoadingGoUp: true })
        }
        if(this.state.folders.length  > 1)
        {
            notification["error"]({
                message: "Error!",
                duration: 10,
                description: `Cannot go up for multiple folders`
            })
        }
        else if(this.state.folders.length  < 1)
        {
            notification["error"]({
                message: "Error!",
                duration: 10,
                description: `No folders to go up!`
            })
        }
        else{
            this.setState({expandedKeys:[], mode: "repo_explorer"});
            axiosInstance.post("/results/go_up",{
            svn_link:this.state.folders[0].id,
        }).then((response) => {
            if(Array.isArray(response.data))
            {
                let antified_data = this.antifyData(response.data);
                const folders = antified_data;
                this.setState({folders})
                this.setState({loadedKeys: []})
                this.setState({expandedKeys:[]});
            }
            else{
                notification["warning"]({
                    message: "Warning!",
                    duration: 10,
                    description: `No folders to go up!`
                })
            }
            this.setState({ iconLoadingGoUp: false })
               })
               .catch((err) => {
                    console.warn('ERR TreeQuery:', err);
               });
            }
    }

    get_revisions(selected_keys= [])
    {
      var svn_id = ""
      if (this.state.mode == "repo_browser" )
      {
        if(selected_keys && selected_keys.length)
        {
          svn_id = this.state.selectedKeys[0]
        }
        else
        {
          svn_id = this.state.folders[0].id
        }
      }
      else if (this.state.folders && this.state.folders.length){
        svn_id = this.state.folders[0].id
      }
      else{
        return
      }
      this.setState({revisionLoading:true})
      axiosInstance.post("/results/get_revisions",{
            svn_link:svn_id,
        }).then((response) => {
          this.setState({revisions:response.data})
          this.setState({revisionLoading:false})
            })
            .catch((err) => {
                    console.warn('ERR TreeQuery:', err);
               });
    }      
    checkRecursivelyAndGetObjext(folder_list, compare_link)
    {
        var return_obj = null
        //console.log(folder_list)
        //console.log(compare_link)
        for(var i=0; i < folder_list.length; i++ ) 
        {
            if (folder_list[i].id == compare_link)
            {
                return_obj = folder_list[i]
            }
            else if (folder_list[i].children.length)
            {
                return_obj = this.checkRecursivelyAndGetObjext(folder_list[i].children,compare_link)
            }
            if(return_obj)
            {
                break;
            }
        }
        return return_obj
    }
    checkForLoadedKeys()
    {
        console.log("We are go!!")
    }
    onLoadData(treeNode)
    {
        //debugger;
        var { folders } = this.state;
        var current_treenode = this.checkRecursivelyAndGetObjext(folders,treeNode.props.dataRef.id)
        //this.setState({loadedKeys:treeNode})
        //console.log(current_treenode)
        return new Promise((resolve) => {
            axiosInstance.post("/results/get_folders",{
                svn_link:treeNode.props.dataRef.id,
                public_permission: treeNode.props.dataRef.permissionObtained,
                allowed_links: [],
                revision:this.state.currentRevision,
                mode: this.state.mode
            }).then((response) => {                       for(var i=0; i < response.data.length; i++ )
                       {
                           let cleaned_tree_item = this.cleanTreeItem(response.data[i])
                           //console.log(cleaned_tree_item)
                           if(cleaned_tree_item)
                           {
                               current_treenode.children.push(cleaned_tree_item)
                           }
                       }
                       this.setState({folders});
                       this.setState({
                        loadedKeys:[...this.state.loadedKeys, treeNode.props.dataRef.id]
                      });
                        resolve();
                   })
                   .catch((err) => {
                        console.warn('ERR TreeQuery:', err);
                   });
          });}

    antifyData(d) {
        let antified_data = [];
        let roots=[];
        for(var i=0; i < d.length; i++ ) {
            let cleaned_tree_item = this.cleanTreeItem(d[i]);
            antified_data.push(cleaned_tree_item);
            roots=[cleaned_tree_item]
        }
        var current_path_to_commit = null;
        if(roots.length)
        {
            current_path_to_commit = roots[0].id
        }
        this.setState({roots,current_path_to_commit})
        return antified_data
    }
    cleanTreeItem(treeItem) {
        // Cleans single tree item.
       
        let id = treeItem.id;
        let title = treeItem.text;
        if(treeItem.map_staus)
        {
            title = treeItem.text;
        }
        let parent = treeItem.parent;
        let img = treeItem.icon;
        let isNode = treeItem.children_status;
        let permissionObtained = treeItem.public_permission;
        let mapped_status = treeItem.map_staus;
        let size = treeItem.size;
        const children = [];
        if (isNode)
        {
            for( var j=0; j < treeItem.children.length; j++) {
            var child = this.cleanTreeItem(treeItem.children[j])
            if(child)
            {
                children.push(child);
            }
            }
        }
        let cleaned_tree_item = {
        title, id, parent,
            children, img, isNode, permissionObtained, mapped_status, size};
    let currentfolderNamesCache = this.state.folderNamesCache;
    currentfolderNamesCache[cleaned_tree_item.id] = cleaned_tree_item;
    this.setState({folderNamesCache:currentfolderNamesCache})
    if(mapped_status)
    {
        this.setState({
            public_folders_only:[...this.state.public_folders_only, id]
          });  
    }
    if(children.length)
    {
        this.setState({
            loadedKeys:[...this.state.loadedKeys, id]
          });   
    }    
        return cleaned_tree_item;
    }
    populateProducts() {
        if(!this.state.iconLoading && this.state.ticket_id){
            this.setState({ iconLoading: true });
        }
        //TODO change URL
        if (this.state.ticket_id != null)
        {
            this.setState({
                loadedKeys:[]
              });
            axiosInstance.get('results/'+this.state.ticket_id)
            .then(res => {
                let antified_data = this.antifyData(res.data);
                const folders = antified_data;
                //console.log(folders)
                this.setState({folders})
                //console.log(this.state.folders)
                this.setState({ iconLoading: false });
                //this.setState({expandedKeys: []})
                this.get_revisions()
                if(folders && folders.length)
                    this.setState({expandedKeys:[folders[0].id]});
                //    this.onTreeExpand(folders[0].id)
                
            })
            .catch(error => {
                console.log(error)
                notification["error"]({
                    message: "Error!",
                    duration: 10,
                    description: `Unable to retrieve data! This operation might have failed due to
                    1.  Check your internet connection!
                    2.  Invalid Redmine Id
                    3.  Redmine Ticket is not linked to the SVN repo
                    If you still face the issue, please contact the maintainer in the footer
                    `
                })
                this.setState({ iconLoading: false });
            })
        }
    }
    populateProductsforRoot() {
        if(!this.state.iconBrowseLoading){
            this.setState({ iconBrowseLoading: true });
        }
    //TODO change URL
    axiosInstance.get('results/root')
    .then(res => {
        let antified_data = this.antifyData(res.data);
        const folders = antified_data;
        this.setState({folders})
        this.setState({ iconBrowseLoading: false });
    })
    .catch(function (error) {
        //console.log(error)
        notification["error"]({
            message: "Error!",
            duration: 10,
            description: `Unable to retrieve data! Check your coneection!`
        })
    })
    
    }
    populateProductsforFolder(svn_link) {
        if(!this.state.iconLoading && this.state.guestUser){
            this.setState({ iconLoading: true });
        }
        if(!this.state.iconBrowseLoading){
            this.setState({ iconBrowseLoading: true });
        }
 axiosInstance.post('results/for_link',{
        svn_link:svn_link,
    })
    .then(res => {
        let antified_data = this.antifyData(res.data.data);
        let ids = res.data.ids;
        this.setState({ticket_id:ids}) 
        const folders = antified_data;
        this.setState({folders})
        this.setState({ iconBrowseLoading: false });
        this.get_revisions()
        //console.log(this.state.expandedKeys)
        if(folders && folders.length)
            this.setState({expandedKeys:[folders[0].id]});
        if(this.state.guestUser)
        {
            this.setState({ iconLoading: false });
        }
    })
    .catch(function (error) {
        //console.log(error)
        notification["error"]({
            message: "Error!",
            duration: 10,
            description: `Unable to retrieve data! Check your coneection!`
        })
    })
    }
    //setupBeforeUnloadListener = () => {
    //    window.addEventListener("beforeunload", (ev) => 
    //    {  
    //        ev.preventDefault();
    //        return ev.returnValue = 'Are you sure you want to close?';
    //    });
    //    console.log("added 4!!")
    //};

    componentDidMount() {
        this.populateProducts();
        const selectedKeys = null;
        this.setState({selectedKeys});
        //this.get_revisions()
        //window.addEventListener("beforeunload", (ev) => 
        //{  
        //    ev.preventDefault();
        //    return ev.returnValue = 'Are you sure you want to close?';
        //});
    }
    componentDidUpdate(prevProps,prevState)
    {
        //console.log(prevState)
    }
    componentWillUnmount()
    {
        console.log("Here We are")
    }
    handleLogin(event, form) {
        event.preventDefault();
        form.validateFields((err, values) =>{
            if (!err) {
                axiosInstance.post("/login", {
                    username: values["userName"],
                    password: values["password"],
                    remember_me: values["remember"]
                })
                    .then(response => {
                        notification["success"]({
                            message: "Success!",
                            description: `Logged in as ${values['userName']}!`
                        });
                        const isLoggedIn = true;
                        const currentPage = "1"
                        this.setState({ isLoggedIn, currentPage})
                        axiosInstance.get("/check_login")
                        .then(res => {
                            const userName = res.data.username;
                            //For testing 
                            const guestUser = res.data.guest;//false;
                            const allowRevision = res.data.allow_revisions;//false;
                            this.setState({userName ,guestUser,allowRevision})
                            if(this.state.issue_id)
                                this.populateProducts()
                        })
                    })
                    .catch(function (error) {
                        //console.log(error)
                        notification["error"]({
                            message: "Error!",
                            description: `Unable to login as ${values['userName']}!`
                        })
                    })
            }
        })
    }
    
    onDropdownSelected(e) {
        this.setState({currentRevision:e})
        this.populateProducts()
     }
    onMenuSelect(i) {
        let currentPage = i.selectedKeys;
        if (currentPage[0] == '5') {
            this.setState({currentPage});
        }
        if (currentPage[0] == "6") {
                //console.log("Logging out!")
                axiosInstance.get("/logout")
                    .then( res => {
                        const isLoggedIn = false;
                        this.setState({isLoggedIn})
                        notification["success"]({
                            message: "Success",
                            description: "Successfully logged out!"
                        })
                    })
                    .catch(error =>{
                        //console.log(error);
                    })
            }
            if (currentPage[0] == "8") {
                const steps = [
                    {
                        intro: "Welcome to Eureka - SDM Browser! This tool will help you in linking and sharing of your results!"
                    },
                    {
                        element: document.querySelectorAll("#treeButton")[0],
                        intro: "Eureka - SDM Browser is a tool to share the result data!",
                    },
                    {
                        element: document.querySelectorAll("#loginPage")[0],
                        intro: "Log Out of the page!",
                    },
                    {
                        element: document.querySelectorAll("#downloadData")[0],
                        intro: "Download the selected folders of the tree",
                    },
                    {
                        element: document.querySelectorAll("#svnLinker")[0],
                        intro: "Go to the svn linker page to check which svn folder is linked to the ticket",
                    },
                    {
                        element: document.querySelectorAll("#redmine")[0],
                        intro: "Go to to the redmine ticket of the particular id",
                    },
                    {
                        element: document.querySelectorAll("#shareLink")[0],
                        intro: "Share the link of the selected and already shared folders(that are listed in public_data.json file).",
                    },
                    {
                        element: document.querySelectorAll("#resultLink")[0],
                        intro: "Link your results to redmine",
                    },
                    {
                        element: document.querySelectorAll("#publicData")[0],
                        intro: "Write public_data.json file and commit it to svn, which will make your folders public! Select the files and folders and click on this button",
                    },
                    
                    {
                        element: document.querySelectorAll("#username")[0],
                        intro: "Current User Name",
                    },
                    {
                        element: document.querySelectorAll("#submitButton")[0],
                        intro: "To submit the redmine id and retrive the result data",
                    },
                    {
                        element: document.querySelectorAll("#redminTicketInput")[0],
                        intro: "Redmine ticket id whose mapped results will be retrieved",
                    },
                    {
                        element: document.querySelectorAll("#treeComponent")[0],
                        intro: "Folder structure of the shared results. If the folder has background of different color it means it has been shared"
                    },
                ]
                var intro = introJs();
                intro.setOptions({ steps });
                intro.setOption("showProgress", true);
                // intro.addHints();
                this.setState({ intro });
                intro.start();
            }
        }
    onInputChange(e)
    {
        const ticket_id = e.target.value;
        this.setState({ticket_id});
    }

    onInputSubmit()
    {

        this.setState({ iconLoading: true, mode: "normal"});
        this.populateProducts()
    }

    onBrowseButton()
    {
        this.setState({ mode: "repo_browser", revisions:[]});
        this.populateProductsforRoot()
    }
    onPressEnter()
    {
        this.setState({ iconLoading: true });
        this.populateProducts()
    }
    onSvnLinker()
    {
        window.location = "http://dllohsr255.driveline.gkn.com:27500/issue/"+ this.state.ticket_id;
    }
    onRedmine()
    {
        window.location = "http://lohsr218.driveline.gkn.com/issues/"+ this.state.ticket_id;
    }
    onLinkResults()
    {
        if(!this.state.ticket_id)
        {
            notification["error"]({
                message: "Error!",
                duration: 10,
                description: `Results cannot be linked without redmine ticket id!`
            })
        }
        else
        {
        let checked_data = []
        for(var i = 0 ; i < this.state.checkedKeys.length ; i++ )
        {
          var checkedNode = this.state.folderNamesCache[this.state.checkedKeys[i]]
          checked_data.push({
                            svn_link: checkedNode.id,
                            parent: checkedNode.parent
                          })
        }
        var root_folder = ""
        if (this.state.mode == "repo_browser")
        {
            notification["error"]({
                message: "Error!",
                duration: 10,
                description: `Explore to the required folder to create the share link`
            })
        }
        else{
            root_folder = this.state.roots[0].id
        }
        
        //console.log("Link Code Goes here!!")
        var payload = {
            issue_id : this.state.ticket_id,
            data:  checked_data,
            revision:this.state.currentRevision,
            root_folder:root_folder
        }
        axiosInstance.post("/link/",payload).then((response) => {
            notification["success"]({
                message: "Success!",
                description: `Ticket has been linked!!!`
            });
               })
               .catch((err) => {
                    //console.warn('ERR TreeQuery:', err);
               });}
    }
    onWritePublicData()
    {
        console.log("Here we go again!!!")
        if(!this.state.ticket_id)
        {
            notification["error"]({
                message: "Error!",
                duration: 10,
                description: `Cannot write public data if it has a valid Redmine ticket Id`
            })
        }
        else{
        let checked_data = []
        for(var i = 0 ; i < this.state.checkedKeys.length ; i++ )
        {
            var checkedNode = this.state.folderNamesCache[this.state.checkedKeys[i]]
          checked_data.push({
                            svn_link: checkedNode.id,
                            parent: checkedNode.parent
                          })
        }
        var payload = {
            issue_id : this.state.ticket_id,
            data:  checked_data,
        }
        axiosInstance.post("/write/", payload)
        .then(res => {
            notification["success"]({
                message: "Success!",
                description: `Successfully written data`
            });
        }
        )
    }
    }
    onGenerateShareLink(option)
    {
        if(option == 4 || option == 5)
        {
            if(!this.state.ticket_id)
            {
            notification["error"]({
                message: "Error!",
                duration: 10,
                description: `Share link can be generated if it has a valid Redmine ticket Id`
            })
            }
        }
        if(this.state.ticket_id.includes(","))
        {
            notification["error"]({
                message: "Error!",
                duration: 10,
                description: `Cannot generate share link for multiple tickets`
            })
        }
        else{
            
        let checked_data = []
        for(var i = 0 ; i < this.state.checkedKeys.length ; i++ )
        {
        var checkedNode = this.state.folderNamesCache[this.state.checkedKeys[i]]
          checked_data.push({
                            svn_link: checkedNode.id,
                            parent: checkedNode.parent
                          })
        }
        var payload = {
            issue_id : this.state.ticket_id,
            data:  checked_data,
            revision:this.state.currentRevision,
            option: option,
            root_folder: this.state.roots[0].id
        }
        axiosInstance.post("/share/link/", payload)
        .then(res => {
            const token = res.data.token;
            //const link = window.location.href + 
            const key = `open${Date.now()}`;
            const link = window.location.href.split('?')[0] + "share/link/v2/" + token
            const copyToClipboard = () => {
                notification.close(key)
                //navigator.permissions.query({
                //    name: 'clipboard-read'
                //  }).then(permissionStatus => {
                //    // Will be 'granted', 'denied' or 'prompt':
                //    console.log(permissionStatus.state);
                //    navigator.clipboard.writeText(link);
                //  })
                window.prompt("Copy to clipboard: Ctrl+C, Enter", link);
                
              };
            const btn = (
                <Button type="primary" size="small" icon="copy" onClick={() => copyToClipboard()}>
                  Copy
                </Button>
            );
           
            notification.open({
                message: 'Share Link',
                description:
                link,
                btn,
                key
              });
        })
        return null
    }
    }
    progressBarCancel(e)
    {
        axiosInstance.get(`/download/cancel/${this.state.progressBarKey}`)
        .then(res => {
        })
        .catch(error => {
            console.log(error);
        })
        this.setState({progressBarVisible:false})
        clearInterval(this.intervalProgressLoop);
    }
    progressBarOk(e)
    {
        this.setState({progressBarVisible:false, progressBarKey :"", currentProgress:0})
        clearInterval(this.intervalProgressLoop);
    }
    getProgressData(){
        console.log(this.state.progressBarKey)
        axiosInstance.get(`/download/progress/${this.state.progressBarKey}`)
        .then(res => {
            //console.log(res.data)
            var progress = res.data.progress;
            this.setState({currentProgress:progress})
            //console.log(progress)
            if(progress == 100)
            {
                clearInterval(this.intervalProgressLoop);
                this.setState({progressBarVisible:false})
            }
            //console.log(this.state.currentProgress)
        })
        .catch(error => {
            console.log(error);
        })

    }
    onDownloadSubmit()
    {
        //console.log(this.state.checked_nodes);
        let checked_data = []
        if (this.state.checkedKeys.length)
        {
            notification.info({
            message: 'Download',
            duration:3,    
            description:
              'Your download will start shortly!',
           
          });
        this.setState({progressBarVisible:true})
        this.intervalProgressLoop = setInterval(this.getProgressData.bind(this), 1000)
        for(var i = 0 ; i < this.state.checkedKeys.length ; i++ )
        {
          var checkedNode = this.state.folderNamesCache[this.state.checkedKeys[i]]
          checked_data.push({
                            svn_link: checkedNode.id,
                            parent: checkedNode.parent,
                            permission: checkedNode.permissionObtained,
                          })
        }
        const timestamp = Date.now(); // This would be the timestamp you want to format
        var fromattedTimestamp = new Intl.DateTimeFormat('en-US', {year: 'numeric', month: '2-digit',day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit'}).format(timestamp)
        var fromattedTimestamp = fromattedTimestamp.split("/").join("_")
        fromattedTimestamp = fromattedTimestamp.split(":").join("_")
        fromattedTimestamp = fromattedTimestamp.split(" ").join("_")
        fromattedTimestamp = fromattedTimestamp.split(",").join("")
        this.setState({progressBarKey:fromattedTimestamp})
        let payload = {
            issue_id:this.state.ticket_id,
            data: checked_data,
            time_stamp:fromattedTimestamp,
            revision:this.state.currentRevision
          };
        
        axiosInstance.post('/download/',payload,{responseType: 'blob'} )
        .then(response => {
               // Log somewhat to show that the browser actually exposes the custom HTTP header
                    const fileNameHeader = "x-suggested-filename";
                    const suggestedFileName = response.headers[fileNameHeader];
                    const effectiveFileName = (suggestedFileName === undefined? "downloaded_data.zip": suggestedFileName);
                    console.log("Received header [" + fileNameHeader + "]: " + suggestedFileName + ", effective fileName: " + effectiveFileName);
                // This was specifically done for zip files!
                    FileSaver.saveAs(response.data, effectiveFileName);}).catch((response) => {console.error("Could not Download the data from the backend.", response);}
        )
        }
        else
        {
            notification.error({
                message: 'Download',
                duration:3,    
                description:
                  'Nothing to download!',
               
              });
        }
    }
    onSelectPublic = () =>{
        const checkedKeys = [...this.state.public_folders_only]
        this.setState({checkedKeys});
    }
    onSelectAll = () =>{
        //console.log(this.state.folderNamesCache)
        const checkedKeys = [this.state.roots[0].id]
        this.setState({checkedKeys});
    }
    onAddFiles = () =>{
        console.log("Wait will add files!!")
        this.setState({ modalVisible: true, current_path_to_commit: this.state.rightClickElement.props.dataRef.id});
    }
    onExploreFolder = () =>{
        if(!this.state.rightClickElement)
        {
        notification["error"]({
        message: "Error!",
        duration: 10,
        description: `Select a folder to explore`
        })
        return
        }
        var selectedNode = this.state.rightClickElement.props.dataRef
    if(selectedNode.isNode)
    {
        this.setState({ mode: "repo_explorer", revisions:[], expandedKeys:[], ticket_id:"", loadedKeys: []});
        this.populateProductsforFolder(selectedNode.id)

    }
    else {
        notification["error"]({
            message: "Error!",
            duration: 10,
            description: `Select a folder to explore`
            })
    }
       
    }
    onOpenFiles = () =>{
        var checkedNode = null
        if (this.state.checkedKeys.length > 0)
        {
            if(this.state.checkedKeys.length > 1)
            {
            notification["error"]({
                message: "Error!",
                duration: 10,
                description: `Cannot open multiple files`
            })
            return
            }
           
            checkedNode = this.state.folderNamesCache[this.state.checkedKeys[0]]
        }   
        else
        {
           if(this.state.checkedKeys.length == 0 &&  (!this.state.rightClickElement))
            {
            notification["error"]({
                message: "Error!",
                duration: 10,
                description: `Select a file to open`
            })
            return
            }
        
            checkedNode = this.state.rightClickElement.props.dataRef

        }
        if(checkedNode.isNode)
        {
            this.setState({expandedKeys:[...this.state.expandedKeys,checkedNode.id]})
            return
        }
        const timestamp = Date.now();
        var fromattedTimestamp = new Intl.DateTimeFormat('en-US', {year: 'numeric', month: '2-digit',day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit'}).format(timestamp)
        fromattedTimestamp = fromattedTimestamp.split("/").join("_")
        fromattedTimestamp = fromattedTimestamp.split(":").join("_")
        fromattedTimestamp = fromattedTimestamp.split(" ").join("_")
        fromattedTimestamp = fromattedTimestamp.split(",").join("")
        let payload = {
            issue_id:this.state.ticket_id,
            data: [checkedNode],
            time_stamp:fromattedTimestamp,
            revision:this.state.currentRevision
          };
        
        axiosInstance.post('/download/open/',payload )
        .then(response => {
            let win = window.open(response.data.exported_file_path, '_blank');
            win.focus();
          }).catch((response) => {
            console.error("Could not Download the data from the backend.", response);
          })
    }

    handleDataUploadCancel = e => {
        this.setState({ modalVisible: false });
    }
    onDeselectAll=() =>
    {
        const checkedKeys = [];
        //const checked_nodes = [];
        this.setState({checkedKeys});
    }
    render() {
        //console.log("Rendering!!!!")
        const treePageStyle = {
            overflowY: 'auto',
            marginTop: 10,
            paddingLeft: "24",
            paddingRight: "24",
            minHeight:"90vh",
            height: "90%",
            marginBottom: "2%",
            paddingBottom: "2%",
            backgroundImage: window.location.href + "assets/images/absurdity.png",
            backgroundRepeat: "repeat",
        }
        const right_click_menu = (
            <Menu>
            <Menu.Item key="4455" onClick={this.onSelectAll}> <Icon type="select" />Select All</Menu.Item>
            <Menu.Item key="4466" onClick={this.onSelectPublic}><Icon type="carry-out"/>Select Only Public</Menu.Item>
            <Menu.Item key="4477" onClick={this.onDeselectAll}><Icon type="small-dash"/>Deselect All</Menu.Item>
          </Menu>
          );
        const right_click_menu_node = (
            <Menu>
            <Menu.Item key="4479" onClick={this.onOpenFiles}><Icon type="folder-open"/>Open Files</Menu.Item>
            <Menu.Item key="4482" onClick={this.onExploreFolder}><Icon type="folder-open"/>Explore Folder</Menu.Item>
          </Menu>
          );
        const right_click_menu_folder = (
            <Menu>
            <Menu.Item key="4478" onClick={this.onAddFiles}><Icon type="upload"/>Upload Files</Menu.Item>
            <Menu.Item key="4479" onClick={this.onOpenFiles}><Icon type="folder-open"/>Open Files</Menu.Item>
            <Menu.Item key="4482" onClick={this.onExploreFolder}><Icon type="folder-open"/>Explore Folder</Menu.Item>
          </Menu>
          );

        const right_click_menu_deselect_only = (
            <Menu>
            <Menu.Item key="4480" onClick={this.onDeselectAll}><Icon type="small-dash"/>Deselect All</Menu.Item>
            <Menu.Item key="4481" onClick={this.onOpenFiles}><Icon type="folder-open"/>Open Files</Menu.Item>
          </Menu>
          );
          const right_click_menu_deselect_only_node = (
            <Menu>
            <Menu.Item key="4478" onClick={this.onAddFiles}><Icon type="upload"/>Upload Files</Menu.Item>
            <Menu.Item key="4479" onClick={this.onOpenFiles}><Icon type="folder-open"/>Open Files</Menu.Item>
            <Menu.Item key="4482" onClick={this.onExploreFolder}><Icon type="folder-open"/>Explore Folder</Menu.Item>
          </Menu>
          );
        //const 
        const browseRootButton = (<Button type="primary"  onClick={() => this.onBrowseButton()} style={{width:"100%"} } loading={this.state.iconBrowseLoading} id="browseButton" icon="folder-open">Browse All</Button> )
        const submitButton = (<Button type="primary"  onClick={() => this.onInputSubmit()} style={{width:"100%"} } loading={this.state.iconLoading}  disabled={ this.state.isLoggedIn && this.state.guestUser} id="submitButton" >Submit</Button> )
        const treePage = (
            <div style={treePageStyle}>
                <Row gutter={24} align='middle'> 
                    <Col span={ 10
                     } style={{ maxHeight: "80%", padding: 10, overflowX: 'auto', overflowY: 'auto', }}>
                        <Input value={this.state.ticket_id} onChange={(e) => this.onInputChange(e)} onPressEnter={(e) => this.onPressEnter(e)} addonBefore="Redmine Ticket Id:" id ="redminTicketInput" disabled={this.state.guestUser}/> 
                    </Col>
                    <Col span={ 5 } style={{ maxHeight: "80%", padding: 10, overflowX: 'auto', overflowY: 'auto'}}>
                    { submitButton } 
                    </Col>
                    <Col span={ 5 } style={{ maxHeight: "80%", padding: 10, overflowX: 'auto', overflowY: 'auto'}}>
                    {(this.state.isLoggedIn && !this.state.guestUser) ? browseRootButton : null}
                    </Col>
                </Row>
                <Row gutter={24}>
                    {//This is very wrong but we'll move it some day
                    }
                    <Dropdown overlay={ (!this.state.guestUser && this.state.folders.length == 1) ? 
                        ((this.state.rightClickElement? (this.state.rightClickElement.props.dataRef.isNode?right_click_menu_folder:right_click_menu_node):right_click_menu)) 
                        : (this.state.rightClickElement?right_click_menu_deselect_only_node:right_click_menu_deselect_only)} 
                        trigger={['contextMenu']} onVisibleChange = {() =>this.onVisibleChangeOfRightClick()}>
                    <Col
                        span={ 20 }
                        style={{ maxHeight: "100%" , padding: 10, overflowX: 'auto', overflowY: 'auto'}}>
                            <div id="partTree"> 
                                <PartTree
                                    onSelect={ (node) => this.handleSelect(node) }
                                    folders={ this.state.folders }
                                    selectedKeys={ this.state.selectedKeys }
                                    onDragStart = { (e) => this.onTreeDragStart(e)}
                                    onDrop = { (e) => this.onTreeDrop(e)}
                                    expandedKeys={this.state.expandedKeys}
                                    onExpand={ (keys) => this.onTreeExpand(keys) }
                                    onRightClick={ (e) =>this.onRightClick(e) }
                                    isLoggedIn={this.state.isLoggedIn}
                                    autoExpandParent={this.state.autoExpandParent}
                                    onCheck={ (keys,info) => this.onCheck(keys, info) }
                                    onLoadData ={(e) => this.onLoadData(e)}
                                    onClickGoUp ={(e) => this.onClickGoUp(e)}
                                    iconLoadingGoUp = {this.state.iconLoadingGoUp}
                                    onDropdownSelected = {(e) => this.onDropdownSelected(e)}
                                    currentRevision ={this.state.currentRevision}
                                    loadedKeys = {this.state.loadedKeys}
                                    id="treeComponent"
                                    guestuser = {this.state.guestUser} 
                                    checkedKeys={this.state.checkedKeys}
                                    allowRevision={this.state.allowRevision}
                                    onDoubleClick={ (e,info) => this.doDoubleClickAction(e,info)}
                                    mode=  {this.state.mode}
                                    revisions=  {this.state.revisions}
                                    revisionLoading = {this.state.revisionLoading}/>
                                    </div>
                    </Col>
                    </Dropdown>
                </Row>
            </div>
            );
        const menuLoggedOut = (
            <Menu.Item
                key='5'
                id="loginPage"
                style={{float: 'left'}}>
                <Icon
                    type='login' />
                Login
            </Menu.Item>
        )
        const menuLoggedIn = (
            <Menu.Item
                key='6'
                id="loginPage"
                style={{float: 'left'}}>
                <Icon
                    type='logout' />
                Logout
            </Menu.Item>
        )
        const menuDownload = (
            <Menu.Item
                key='2'
                id="downloadData"
                onClick={() => this.onDownloadSubmit()}
                style={{float: 'left'}}>
                <Icon
                    type='download' />
                Download

            </Menu.Item>
        )
        const menuSvnLinker = (
            <Menu.Item
                key='3'
                id="svnLinker"
                onClick={() => this.onSvnLinker()}
                style={{float: 'left'}}>
                < Icon type='link' />
                SVN Linker
            </Menu.Item>
        )
        const menuRedmine = (
            <Menu.Item
                key='4'
                id="redmine"
                onClick={() => this.onRedmine()}
                style={{float: 'left'}}>
                <Icon type="issues-close" />
                Back to Redmine
            </Menu.Item>
        )
        const generateShareLinkSubMenu = (
            <Menu >
              <Menu.Item key="4411" onClick={() => this.onGenerateShareLink(1)}>Preselected only with current version</Menu.Item>
              <Menu.Item key="4412" onClick={() => this.onGenerateShareLink(2)}>Preselected only with latest version</Menu.Item>
              <Menu.Item key="4413" onClick={() => this.onGenerateShareLink(3)}>Preselected only with all version</Menu.Item>
              <Menu.Item key="4414" onClick={() => this.onGenerateShareLink(4)}>Public with current version(Default)</Menu.Item>
              <Menu.Item key="4415" onClick={() => this.onGenerateShareLink(5)} >Public with all version</Menu.Item>
            </Menu>
          );
        const menuShare = (
            <Menu.Item
            key='7'
            id="shareLink"
            style={{float: 'left'}}>
            <Dropdown overlay={generateShareLinkSubMenu}>
            <a className="ant-dropdown-link" onClick={e => e.preventDefault()}>
            Generate share link <Icon type="share-alt" />
            </a>
          </Dropdown>
          </Menu.Item>
        )
        const helpContent = (
            <p>Click this button to begin the interactive tutorial to using this tool.</p>
        )
        const menuUserName = (
            <Menu.Item
                key='9'
                id="username"
                style={{float: 'left'}}>
                <Icon type="user" />
                {this.state.userName}
            </Menu.Item>
        )
        const menuHelp = (
            <Menu.Item
                style={{ fontSize: "18px", color: "#99e", marginBottom: "1.5rem", verticalAlign: "middle" }}
                key='8'
                style={{float: 'left'}}>
                <Popover content={helpContent}>
                    <Icon
                        theme="filled"
                        type="question-circle"
                        className="helpButton"
                        data-hint="Click here to learn how to use this page"
                    />
                </Popover>
            </Menu.Item>
        )
        const menuLink = (
            <Menu.Item
            key='10'
            id="resultLink"
            onClick={() => this.onLinkResults()}
            style={{float: 'left'}}>
            <Icon type="link" />
                Link Results
            </Menu.Item>
        )
        const menuPublicData = (
            <Menu.Item
            key='11'
            id="publicData"
            onClick={() => this.onWritePublicData()}
            style={{float: 'left'}}>
            <Icon type="pushpin" />
                Write Public Data
            </Menu.Item>
        )
        const menu = (
            <Menu
                theme='dark'
                mode='horizontal'
                defaultSelectedKeys={['1']}
                selectedKeys={[this.state.currentPage]}
                style={{ lineHeight: '64px' }}
                onSelect={(i) => this.onMenuSelect(i)}>
                <Menu.Item
                    key='1'
                    id="treeButton"
                    style={{float: 'left'}}
                >
                Eureka - SDM Browser
                </Menu.Item>
                
                {(this.state.isLoggedIn && !this.state.guestUser) ?  menuShare : null }
                {(this.state.isLoggedIn && !this.state.guestUser) ?  menuPublicData : null }
                {(this.state.isLoggedIn && !this.state.guestUser) ?  menuLink : null }
                {this.state.isLoggedIn ? menuDownload : null}
                {this.state.isLoggedIn ? menuHelp : null}
                {this.state.isLoggedIn ? menuUserName:null}
                {this.state.isLoggedIn ? menuLoggedIn : menuLoggedOut}
                {(this.state.isLoggedIn && !this.state.guestUser) ? menuSvnLinker : null}
                {this.state.isLoggedIn ? menuRedmine : null}
            </Menu>
        )
      
        const header = (
            <Header className="header">
                <div className="logo" />
                {/* How do I set up the logo in the right way?
                        I'm using a hack right now. */}
                {menu}
            </Header>
        )
        const progressDialog = (
            <Modal
            title="Download"
            visible={this.state.progressBarVisible}
            onOk={(e) => this.progressBarOk(e)}
            onCancel={(e) => this.progressBarCancel(e)}
          >
            <p>{"Your download is in progress. Please wait!!"}</p>
            <Progress percent={this.state.currentProgress} status="active" />
          </Modal>
        )
        const guestUserLoading = ( 
            <Spin tip="Loading..." spinning={this.state.iconLoading}>
        </Spin>)
         const dataUpload = (
            <DataUploadPage 
            visible = {this.state.modalVisible}
            onCancel = {this.handleDataUploadCancel}
            current_path_to_commit = {this.state.current_path_to_commit}/>)
        let displayedPage;
        if (! this.state.isLoggedIn) {

                // See https://ant.design/components/form/#components-form-demo-normal-login
                // to understand what this is doing.
                const WrappedLoginPage = Form.create({name: "normal_login"})(LoginPage);
                const LoginProps = {
                    style: {
                        width: '50%',
                        height: "50%",
                        marginTop: "10%",
                        marginLeft: '25%',
                        marginRight: '25%',
                        marginBottom: "25%",
                        paddingTop: '5%',
                        paddingBottom: "5%",
                        paddingLeft: '10%',
                        paddingRight: '10%',
                        // border: "2px solid red",
                        resize: "none"
                    }
            }
            displayedPage = (
                    <div {...LoginProps}>
                        <WrappedLoginPage
                            handleLogin = {(e,f) => this.handleLogin(e,f)}
                            style={{resize: "none"}}
                            isLoggedIn={this.state.isLoggedIn}/>
                    </div>
                )
            }
        else{
            displayedPage = treePage;
        }
        return (
            <Layout className="layout" style={{overflowY: "hidden"}}>
                {(this.state.isLoggedIn && this.state.guestUser)?guestUserLoading:null}
                {header}
                {dataUpload}
                {progressDialog}
                <Content style={{paddingLeft: '0.5rem', backgroundColor: '#eaeae8'}}>
                    {displayedPage}
                </Content>
                <ResultLinkerFooter />
            </Layout>
        );
    }
}
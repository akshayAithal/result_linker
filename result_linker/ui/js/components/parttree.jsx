import React from 'react';
import { Input, Icon, Tree, Avatar, DirectoryTree, Row, InputNumber  } from 'antd';
import { Col } from 'antd';
const { TreeNode } = Tree;
import { Select } from 'antd';
import { Button } from 'antd';
const { Option } = Select;
const Search = Input.Search;
import axios from 'axios';
import { List, Typography } from 'antd';

const axiosInstance = axios.create({
  baseURL: window.location.href ,
  //proxy: true
});

import newId from './newid';

let prevent = false;
let timer = 0;
let delay = 200;

export class PartTree extends React.Component {
  constructor(props) {
    super(props);
    //this.state = {
    //  revisions:[]
    //}
  }
  renderTreeNodes = data => data.map((item) => {

      /**
       * Helper method used to render each node.
       * NOTE: This is recursive.
       */
      if (item.children) {
        var title = " " + item.title
        if (item.size && item.size.length)
        {
          title = " " + item.title +" (Size: "+ item.size + ")"//<span style={{ float:"right"}}>item.size</span>
        }
        return (
          <TreeNode
            title={title} 
            key={item.id}
            icon={<Avatar size='small' shape='square' src={window.location.href +'assets/images/'+item.img}  />}
            dataRef={item}
            style={(!this.props.guestuser && item.mapped_status)?
              {backgroundColor: "#add8e6", backgroundImage: window.location.href + 'assets/images/absurdity.png'}
              //{backgroundColor: "#fff", backgroundImage: window.location.href + 'assets/images/absurdity.png'}
              :{backgroundColor: "#fff", backgroundImage: window.location.href + 'assets/images/absurdity.png'}}
            isLeaf= {!item.isNode}
            >
            {this.renderTreeNodes(item.children)}
          </TreeNode>

        );
      }
      return <TreeNode {...item}></TreeNode>;
  })
  componentDidUpdate(prevProps,prevState)
  {
    //console.log(prevProps)
    //console.log(prevState)
    //console.log(this.props.folders)
    //if (this.props.folders !== prevProps.folders)
    //{
    //  var svn_id = ""
    //  if (this.props.mode == "repo_browser" )
    //  {
    //    if(this.props.selectedKeys && this.props.selectedKeys.length)
    //    {
    //      svn_id = this.props.selectedKeys[0]
    //    }
    //    else
    //    {
    //      svn_id = this.props.folders[0].id
    //    }
    //  }
    //  else{
    //    svn_id = this.props.folders[0].id
    //  }
    //  
    //  axiosInstance.post("/results/get_revisions",{
    //        svn_link:svn_id,
    //    }).then((response) => {
    //      this.setState({revisions:response.data})
    //        })
    //        .catch((err) => {
    //                console.warn('ERR TreeQuery:', err);
    //           });
    //}      
  }
  createSelectItems() {
    let items = [];   
    if(this.props.revisions)      
    {
      for (let i = 0; i <= this.props.revisions.length; i++) {             
         items.push(<Option key={newId()} value={String(this.props.revisions[i])}>{this.props.revisions[i]}</Option>);            //what props are currently passed to the parent component
    }
  }
    return items;
}  

  render() {
    //console.log(this.state.revisions)
    //console.log(this.props.allowRevision)
    //console.log(!this.state.revisions.length || !this.props.allowRevision)
    return (
      <div id={this.props.id}>
        <Row>
        <Button type="primary" disabled={!this.props.folders.length || this.props.guestuser} onClick={this.props.onClickGoUp} loading={this.props.iconLoadingGoUp} icon="up-circle">
        Go Up
        </Button>
        <span style={{ float:"right"}}>
        Revision : 
        <Select placeholder="Revison" disabled={!this.props.revisions.length || !this.props.allowRevision || this.props.revisionLoading} style={{ width:400}} onChange={this.props.onDropdownSelected} 
        key={newId()} defaultValue = {this.props.currentRevision ? this.props.currentRevision: (this.props.revisions.length?this.props.revisions[0]:null)} loading={this.props.revisionLoading}>
        {this.createSelectItems()}
        </Select>
        </span>
        </Row>
        <Row>
        <div id="folderTree"   style={{ height:'75vh' , padding: 10, overflowX: 'auto', overflowY: 'auto'}}> 
        <Tree
          showIcon
          checkable = {this.props.mode != "repo_browser"}
          autoExpandParent={this.props.autoExpandParent}
          onExpand={this.props.onExpand}
          expandedKeys={this.props.expandedKeys}
          onSelect={this.props.onSelect}
          selectedKeys={this.props.selectedKeys}
          onRightClick={this.props.onRightClick}
          onCheck={this.props.onCheck}
          loadData={this.props.onLoadData}
          loadedKeys ={this.props.loadedKeys}
          checkedKeys= {this.props.checkedKeys}
          onDoubleClick= {this.props.onDoubleClick}
        >
        {this.renderTreeNodes(this.props.folders)}
        </Tree>
        </div>
        </Row>
        </div>
    );
  }
}


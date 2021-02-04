import React from 'react';
import {
    Form, Icon, Input, Button, Checkbox, notification, Modal, message, Upload
} from 'antd';
import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: window.location.href 
});

export const DataUploadForm = Form.create({ name: 'form_in_modal' })(


  // eslint-disable-next-line
  class extends React.Component {
    render() {
      const { visible, onCancel, onCreate, form, confirmLoading} = this.props;
      const { getFieldDecorator } = form;
      //console.log(this.props);
      const normFile = e => {
      //console.log('Upload event:', e);
      //if (Array.isArray(e)) {
      //  return e;
      //}
      //const status = info.file.status;
      //console.log(status)
      //return e && e.fileList;
      };
    //const uploadProps = {
    //  name: 'file',
    //  action: window.location.href +'api/v1/data/',
    //  disabled: true,
    //  onChange(info) {
    //      const status = info.file.status;
    //      if (status !== 'uploading') {
    //          console.log("Not uploading")
    //          // What is this for?
    //          // console.log(info.file, info.fileList);
    //      }
    //      if (status === 'done') {
    //          let reason = info.file.response[0].reason;
    //          if (info.file.response[0].success)
    //          {
    //              Modal.success({
    //              title: "Success!",
    //              content: `${info.file.name} file uploaded successfully. ${reason}`
    //          });
    //          window.reload();
    //          console.log("Refreshed the data!")
    //      }
    //      else
    //      {
    //          Modal.error({
    //              title: "Error!",
    //              content: `Unable to upload "${info.file.name}." ${reason}`
    //          });
    //      }
    //      } else if (status === 'error') {
    //          let reason = info.file.response[0].reason;
    //          Modal.error({
    //              title: "Error!",
    //              content: `Unable to upload "${info.file.name}." ${reason}`
    //          });
    //      }

    //  },
    //
      return (
        <Modal
          visible={visible}
          title="Data Upload"
          okText="Submit"
          onCancel={onCancel}
          cancelText="Close"
          onOk={onCreate}
          confirmLoading={confirmLoading}
        >
        <Form layout="vertical">
          <Form.Item label="SVN Path">
      {this.props.current_path_to_commit}
          </Form.Item>
          <Form.Item label="Message">
              {getFieldDecorator('message', {
                rules: [{ required: true, message: 'Please input the message for commit!' }]
                , initialValue:"Commit from SVN Linker",
              })(<Input />)}
            </Form.Item>
          <Form.Item label="Upload" style={{ height: "35vh", paddingBottom: "5vh"}}>
          {getFieldDecorator('dragger', {
            valuePropName: 'files',
            getValueFromEvent: this.normFile,
          })(
            <Upload.Dragger name="files" action={window.location.href +'results/update_data'}
            >
              <p className="ant-upload-drag-icon">
                <Icon type="inbox" />
              </p>
              <p className="ant-upload-text">Click or drag file to this area to upload</p>
              
            </Upload.Dragger>,
          )}
        </Form.Item>
        </Form>
        </Modal>
      );
    }
  },
);

export class DataUploadPage extends React.Component {
  state = {
    confirmLoading: false,
  };
  saveFormRef = formRef => {
    this.formRef = formRef;
  };

  handleDataSubmit = e => {
    const { form } = this.formRef.props;
    var commit_message = "";
    //console.log(message)
    this.setState({confirmLoading:true});
    form.validateFields((err, values) => {
      if (err) {
        return;
      }
      commit_message = values.message;
      console.log('Received values of form: ', values);
      console.log('Type: ', typeof(values));
      axiosInstance.post(
        window.location.href +'results/commit_data',
        { svn_link:this.props.current_path_to_commit, commit_message:commit_message,})
        .then(res => {

            if (res.data["success"]) {
                message.success('File has been committed!!');
                form.resetFields();
            } else {
              message.error('Issue with the commit!');
              form.resetFields();
            }
            this.setState({confirmLoading:false});
        })
        .catch(error => {
            console.log(error.response)
            this.setState({confirmLoading:false});
        })
      form.resetFields();
     
    });
  };

  render() {
    return (
      <div>
        <DataUploadForm
          wrappedComponentRef={this.saveFormRef}
          visible={this.props.visible}
          onCancel={this.props.onCancel}
          onCreate={this.handleDataSubmit}
          current_path_to_commit={this.props.current_path_to_commit}
          confirmLoading={this.state.confirmLoading}
        />
      </div>
    );
  }
}
